from django.core.management.base import BaseCommand
from django.db import IntegrityError
from apps.content.models import Site, Post  # Adjust 'myapp' to your actual app name
from newspaper import Article
import feedparser  # You might need to install feedparser

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

                if not Post.objects.filter(link=entry.link).exists():
                    post = Post(
                        title=article.title,
                        description=article.meta_description,
                        content=article.text,
                        date_published=article.publish_date,
                        link=entry.link,
                        site=site
                    )
                    try:
                        post.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully saved article: {article.title}'))
                    except IntegrityError as e:
                        self.stdout.write(self.style.ERROR(f'Error saving article: {e}'))
