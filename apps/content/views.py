from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404

from .forms import SiteForm, PostEditForm
from .models import Site, Post, Topic, Tool, Tag


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
    topics = Topic.objects.all().order_by('name')  # Query all topics to pass to the form
    tags = Tag.objects.all()  # Query all topics to pass to the form

    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            saved_post = form.save(commit=False)  # Save the form but not the m2m data yet

            # Handle the many-to-many topics field manually
            topics_ids = request.POST.getlist('topics')  # 'topics' should match the name attribute in your select field
            saved_post.save()  # Save the instance before assigning many-to-many relationships

            if topics_ids:
                saved_post.topics.clear()  # Remove any existing associations
                for topic_id in topics_ids:
                    try:
                        topic = Topic.objects.get(id=topic_id)
                        saved_post.topics.add(topic)
                    except Topic.DoesNotExist:
                        pass  # Handle invalid topic IDs if necessary

            form.save_m2m()  # Now save the rest of the many-to-many data

            if request.htmx:
                # If the post is still valid, return its updated representation
                return render(request, 'components/post-list.html', {'post': saved_post})
            else:
                return redirect('post_view', post_title_slug=saved_post.slug)
    else:
        form = PostEditForm(instance=post)

    # Pass the topics queryset to the template
    return render(request, 'content/partials/post-edit.html', {'form': form, 'post': post, 'topics': topics, 'tags':tags})


def post_view(request, post_title_slug):
    # Find a post that matches the slugified title
    for post in Post.objects.all():
        if slugify(post.title) == post_title_slug:
            return render(request, 'content/post-view.html', {'post': post})

    # If no post is found, return a 404 response
    return HttpResponseNotFound('Post not found')




def topic_page(request, tag_slug):
    # Retrieve the tag object
    tag = get_object_or_404(Topic, slug=tag_slug)

    # Filter posts by the tag name or slug
    posts_list = Post.objects.filter(topics__name=tag.name).order_by('-date_published')

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

    # Filter tools by the tag name or slug
    tools = Tool.objects.filter(topics__name=tag.name).order_by('title')

    return render(request, 'content/topic-page.html', {
        'posts': posts,
        'tools': tools,
        'tag': tag
    })

# Individual tool page
def tool_page(request, tool_slug):
    tool = get_object_or_404(Tool, slug=tool_slug)
    return render(request, 'content/tool-page.html', {'tool': tool})