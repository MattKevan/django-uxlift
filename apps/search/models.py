from django.db import models
from apps.content.models import Post

class Chunk(models.Model):
    post = models.ForeignKey(Post, related_name='chunks', on_delete=models.CASCADE)
    chunk_text = models.TextField()
    chunk_vector = models.JSONField(blank=True, null=True)  # Assuming the vector is stored as a list of floats

    def __str__(self):
        return f"Chunk for post {self.post.id}"