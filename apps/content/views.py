from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import HttpResponseNotFound, HttpResponse
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string

from .forms import SiteForm, PostEditForm
from .models import Site, Post, Topic, Tool


@login_required
def submit_url(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            existing_site = Site.objects.filter(url=url).first()
            if existing_site:
                messages.error(request, "A site with this URL already exists.")
            else:
                submitted_site = form.save(commit=False)
                submitted_site.user = request.user
                submitted_site.save()  # This will trigger the logic in the model's save method
                messages.success(request, "Thank you for submitting the site. Details have been fetched and saved.")
                return redirect('home')
    else:
        form = SiteForm()
    return render(request, 'content/submit-site.html', {'form': form})

@login_required
def submit_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            messages.success(request, "Thank you for submitting the post.")
            return redirect('home')  # Redirect to the home page
    else:
        form = PostForm()
    return render(request, 'content/submit-post.html', {'form': form})

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            saved_post = form.save(commit=False)
            saved_post.save()

            topics_ids = request.POST.getlist('topics')  # Correctly retrieves list of topic IDs
            if topics_ids:
                topics = Topic.objects.filter(id__in=topics_ids)
                saved_post.topics.set(topics)  # Efficiently updates the ManyToMany field

            if request.htmx:
                response = render(request, 'common/post-list.html', {'post': saved_post})
                response['HX-Trigger'] = 'postSaved'
                messages.success(request, f"'{saved_post.title}' saved successfully!")
                return response
            else:
                messages.success(request, f"'{saved_post.title}' saved successfully!")
                return redirect('post_view', post_title_slug=saved_post.slug)
    else:
        form = PostEditForm(instance=post)
        topics = Topic.objects.all().order_by('name')  # Ensures topics are ordered alphabetically

    return render(request, 'content/partials/post-edit.html', {'form': form, 'post': post, 'topics': topics})

def post_view(request, post_title_slug):
    # Find a post that matches the slugified title
    for post in Post.objects.all():
        if slugify(post.title) == post_title_slug:
            return render(request, 'content/post-view.html', {'post': post})

    # If no post is found, return a 404 response
    return HttpResponseNotFound('Post not found')


def post_view(request, post_title_slug):
    # Find a post that matches the slugified title
    for post in Post.objects.all():
        if slugify(post.title) == post_title_slug:
            return render(request, 'content/post-view.html', {'post': post})

    # If no post is found, return a 404 response
    return HttpResponseNotFound('Post not found')

@staff_member_required
def unpublish_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    post.status = 'unpublished'
    post.save()
    # Return an empty response for HTMX to remove the post from the listing
    html = render_to_string('common/empty.html', {'post': post})
    return HttpResponse(html)

def topic_page(request, topic_slug):
    # Retrieve the topic object
    topic = get_object_or_404(Topic, slug=topic_slug)

    # Filter posts by the topic name or slug
    posts_list = Post.objects.filter(
        topics__name=topic.name, 
        status__in=['published', '']  # Include posts that are either explicitly marked as published or have a blank status
    ).order_by('-date_published')

    # Set up pagination
    paginator = Paginator(posts_list, 20)  # 20 posts per page

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)

    # Filter tools by the topic name or slug
    tools = Tool.objects.filter(topics__name=topic.name).order_by('title')

    return render(request, 'content/topic-page.html', {
        'posts': posts,
        'tools': tools,
        'topic': topic
    })

# Individual tool page
def tool_page(request, tool_slug):
    tool = get_object_or_404(Tool, slug=tool_slug)
    return render(request, 'content/tool-page.html', {'tool': tool})