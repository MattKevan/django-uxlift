from django.core.management.base import BaseCommand
from apps.content.models import Post
import csv

class Command(BaseCommand):
    help = 'Export Post objects to a CSV file'

    def handle(self, *args, **options):
        filename = "posts_export.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'content', 'link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for post in Post.objects.all():
                writer.writerow({
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'link': post.link
                })

        self.stdout.write(self.style.SUCCESS(f'Successfully exported posts to {filename}.'))
