from django.db import models
from django.conf import settings

from utils.mixins import UniqueSlugMixin
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload
from urllib.parse import urlparse

# Create your models here.
class LearningCategory(models.Model, UniqueSlugMixin):
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(LearningCategory, self.name)
        super(LearningCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
class LearningProvider(models.Model):
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
    category = models.ManyToManyField(LearningCategory)
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