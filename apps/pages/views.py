from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView
from apps.content.models import Post, Topic, Tool, Site
from django.shortcuts import render
from django.db.models import Count

# Home page
class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a query to get the most recent posts
        context['recent_posts'] = Post.objects.filter(status__in=['published', '']).order_by('-date_published')[:10]     
        context['tags'] = Topic.objects.all().order_by('name')  # Similar to your 'tags = Topic.objects.all()' but ordered
        context['tools'] = Tool.objects.all().order_by('-date')[:9]

        return context
    
# News page
def news(request):
    post_list = Post.objects.filter(status__in=['published', '']).order_by('-date_published')  # Assuming posts have a date_posted field to order by
    paginator = Paginator(post_list, 20)  # Show 20 posts per page

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    return render(request, 'pages/news.html', {'posts': posts})

# About page
def about(request):
    return render(request, 'pages/about.html')

# Topics page
def topics(request):
    tags = Topic.objects.all().order_by('name')
    return render(request, 'pages/topics.html', {'tags': tags})

# Tools page
def tools(request):
    tools = Tool.objects.all().order_by('-date')[:9]
    tags = Topic.objects.annotate(num_tools=Count('tool')).filter(num_tools__gt=0).order_by('name')
    return render(request, 'pages/tools.html', {'tags': tags, 'tools':tools})

# Publications page
def sites(request):
    sites = Site.objects.all()
    return render(request, 'pages/sites.html', {'sites': sites})

# Courses page
def sites(request):
    sites = Site.objects.all()
    return render(request, 'pages/courses.html', {'sites': sites})
