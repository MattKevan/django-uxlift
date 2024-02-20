from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils import timezone
from apps.content.models import Site, Post  # Ensure the path matches your project structure
from newspaper import Article
import feedparser  # Ensure feedparser is installed
import dateutil.parser  # You might need to install python-dateutil
import datetime  # Import the datetime module

class Command(BaseCommand):
    help = 'Fetches RSS items and saves them as Posts'

    def handle(self, *args, **options):
        for site in Site.objects.filter(include_in_newsfeed=True):
            self.stdout.write(self.style.SUCCESS(f'Fetching articles for {site.title} from {site.feed_url}'))
            feed = feedparser.parse(site.feed_url)

            for entry in feed.entries:
                article = Article(entry.link)
                article.download()
                article.parse()

                # Convert publish_date to a timezone-aware datetime object
                publish_date = None
                if article.publish_date:
                    # Check if article.publish_date is a string before parsing
                    if isinstance(article.publish_date, datetime.datetime):
                        publish_date = article.publish_date
                    else:
                        publish_date = dateutil.parser.parse(article.publish_date)
                    # Make the datetime object timezone aware
                    if timezone.is_naive(publish_date):
                        publish_date = timezone.make_aware(publish_date, timezone.get_default_timezone())

                if not Post.objects.filter(link=entry.link).exists():
                    post = Post(
                        title=article.title,
                        description=article.meta_description,
                        content=article.text,
                        date_published=publish_date,
                        link=entry.link,
                        site=site
                    )
                    try:
                        post.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully saved article: {article.title}'))
                    except IntegrityError as e:
                        self.stdout.write(self.style.ERROR(f'Error saving article: {e}'))
