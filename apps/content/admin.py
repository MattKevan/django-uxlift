from django.contrib import admin
from .models import Site, Post, Topic, Tool, SiteType

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']

@admin.register(SiteType)
class TopicAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    autocomplete_fields = ['topics']

    list_display = ['title', 'display_topics', 'date_published']
    ordering = ['-date_published']
    
    def display_topics(self, obj):
        return ", ".join([topic.name for topic in obj.topics.all()])
    display_topics.short_description = 'Topics'

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    autocomplete_fields = ['topics']
    search_fields = ['name']
    list_display = ['title', 'display_topics']

    def display_topics(self, obj):
        return ", ".join([topic.name for topic in obj.topics.all()])
    display_topics.short_description = 'Topics'


@admin.register(Site)
class Sitedmin(admin.ModelAdmin):
    #filter_horizontal = ['site_type']    
    search_fields = ['name']
    list_display = ['title', 'include_in_newsfeed']
    def display_sites(self, obj):
        return ", ".join([site.name for site in obj.sites.all()])
    display_sites.short_description = 'Site type'
