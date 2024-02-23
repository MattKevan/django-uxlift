from django.conf import settings
from django.contrib.auth.models import Group
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload
from django.db import models
import requests  # Make sure you have this line
from bs4 import BeautifulSoup
from django.contrib.auth.models import User  # Add this line
from django.utils import timezone
import os
from datetime import date
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from urllib.parse import urlparse
from tinymce import models as tinymce_models
from newspaper import Article

class Topic(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from name
            self.slug = slugify(self.name)

            # Ensure the slug is unique
            original_slug = self.slug
            counter = 1
            while SiteType.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class SiteType(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from name
            self.slug = slugify(self.name)

            # Ensure the slug is unique
            original_slug = self.slug
            counter = 1
            while SiteType.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Site(models.Model):
    STATUS_CHOICES = [
        ('D', 'Draft'),
        ('P', 'Published'),
    ]
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    url = models.URLField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    feed_url = models.URLField(null=True, blank=True)
    site_icon = CloudinaryField('image', null=True, blank=True)
    site_type = models.ManyToManyField(SiteType)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    include_in_newsfeed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def find_feed(self):
        if self.is_valid_url(self.url) and not self.feed_url:
            try:
                response = requests.get(self.url)
                soup = BeautifulSoup(response.content, 'html.parser')
                feed_urls = [link['href'] for link in soup.find_all('link', type='application/rss+xml')]
                if feed_urls:
                    self.feed_url = feed_urls[0]
            except requests.RequestException as e:
                print(f"Error fetching feed for URL '{self.url}': {e}")
                self.feed_url = None

    def find_meta_info(self):
        if self.is_valid_url(self.url):
            try:
                response = requests.get(self.url)
                soup = BeautifulSoup(response.content, 'html.parser')

                if not self.title:
                    meta_title = soup.find("meta", property="og:title") or soup.find("title")
                    if meta_title:
                        self.title = meta_title.get("content", "") or meta_title.text

                if not self.description:
                    meta_description = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
                    if meta_description:
                        self.description = meta_description.get("content", "")
            except requests.RequestException as e:
                print(f"Error fetching meta info for URL '{self.url}': {e}")

    def find_and_save_icon(self):
        if self.is_valid_url(self.url) and not self.site_icon:
            try:
                response = requests.get(self.url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                icon_link = soup.find("link", rel="apple-touch-icon") or soup.find("link", rel="shortcut icon")
                if icon_link:
                    icon_url = icon_link['href']
                    icon_url = urljoin(self.url, icon_url)
                    
                    if icon_url:
                        uploaded_image = upload(icon_url)
                        self.site_icon = uploaded_image.get('public_id')
            except Exception as e:
                print(f"Error fetching or uploading icon for site '{self.title}': {e}")

    def save(self, *args, **kwargs):
        self.find_feed()
        self.find_meta_info()
        self.find_and_save_icon()

        if not self.user_id:
            default_user = get_user_model().objects.get(id=1)
            self.user = default_user

        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Site.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateField(default=date.today)  # Converted to DateField
    date_published = models.DateField(null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    link = models.URLField(max_length=1000)
    image_path = models.URLField(max_length=1000, null=True, blank=True)  # or models.ImageField() depending on how you are handling images
    topics = models.ManyToManyField('Topic', blank=True)  # Assuming 'Topic' is a model for topics
    tags_list = models.TextField(blank=True, null=True)
    content = tinymce_models.HTMLField(null=True, blank=True, default='published')
    STATUS_CHOICES = [
        ('published', 'Published'),
        ('unpublished', 'Unpublished'),
    ]
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='published', blank=True)

    def __str__(self):
        return self.title
    
    def is_published(self):
        return self.status == 'published' or self.status == ''
    
    def fetch_og_image(self):
        try:
            response = requests.get(self.link)
            soup = BeautifulSoup(response.content, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
        except Exception as e:
            print(f"Error fetching OG image for post '{self.title}': {e}")
        return None 
       
    def fetch_article_data(self):
        article = Article(self.link)
        article.download()
        article.parse()
        #article.nlp()

        # Update the Post instance fields
        self.date_published = article.publish_date if article.publish_date else self.date_published
        self.content = article.text if article.text else self.content
        #self.summary = article.summary if article.summary else self.summary

        # Get the og:image and save it to image_path
        if not self.image_path:
            self.image_path = self.fetch_og_image()
                   
    def find_or_create_site(self):
        post_url_parsed = urlparse(self.link)
        post_root_url = f"{post_url_parsed.scheme}://{post_url_parsed.netloc}"
        site, created = Site.objects.get_or_create(url=post_root_url)
        return site

    def save(self, *args, **kwargs):
        # Fetch article data and handle many-to-many fields before the first save
        if not self.pk:  # Check if the instance is not yet saved (has no primary key)
            self.fetch_article_data()
        
        if not self.user_id:
            # Set default user if not provided
            default_user = get_user_model().objects.get(id=1)
            self.user = default_user

        if not self.site:
            self.site = self.find_or_create_site()

        super().save(*args, **kwargs)  # Call the "real" save() method

class Tool(models.Model):
    title = models.CharField(max_length=600)
    description = models.TextField()
    link = models.URLField()
    image = CloudinaryField('image')
    date = models.DateTimeField(default=timezone.now)
    topics = models.ManyToManyField(Topic)
    body = models.TextField()  # This can be used for the full content of the tool
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Tool, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
