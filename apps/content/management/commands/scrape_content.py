import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
import logging
from newspaper import Article, Config
from django.core.management.base import BaseCommand
from apps.content.models import Post  # Ensure this is the correct path to your Post model

# Setup logging
logging.basicConfig(filename='scrape_errors.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Configure newspaper to use custom headers
config = Config()
config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

class Command(BaseCommand):
    help = 'Scrapes articles using newspaper3k with custom headers and updates the content field in Post model'

    def handle(self, *args, **kwargs):
        posts = Post.objects.filter(content__isnull=True)  # Or use content='' to check for empty strings
        total = posts.count()
        processed = 0

        for post in posts:
            self.stdout.write(self.style.NOTICE(f'Processing {post.title}...'))
            try:
                # Initialize Article object with custom configuration using the 'link' field
                article = Article(post.link, config=config)  # Changed from post.url to post.link
                article.download()
                article.parse()

                if article.text:
                    post.content = article.text
                    post.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated {post.title}.'))
                else:
                    logging.info(f'No content found for ID {post.id}, Title: {post.title}')

            except Exception as e:
                logging.info(f'ID: {post.id}, Title: {post.title}, Error: {str(e)}')
                self.stdout.write(self.style.ERROR(f'Error processing {post.title}. Check log for details.'))

            processed += 1
            self.stdout.write(self.style.NOTICE(f'Progress: {processed}/{total}'))

        self.stdout.write(self.style.SUCCESS('Completed updating posts.'))
