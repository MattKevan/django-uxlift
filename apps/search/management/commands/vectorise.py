from django.core.management.base import BaseCommand
from transformers import AutoTokenizer, AutoModel
import torch
from apps.content.models import Post
from apps.search.models import Chunk
from nltk.tokenize import sent_tokenize
import nltk

# Ensure NLTK's punkt tokenizer is downloaded
nltk.download('punkt')

class Command(BaseCommand):
    help = 'Chunks and vectorizes posts, storing the results in the Chunk model'

    def handle(self, *args, **kwargs):
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        model = AutoModel.from_pretrained("bert-base-uncased")

        for post in Post.objects.all():
            # Skip posts that have already been chunked
            if Chunk.objects.filter(post=post).exists():
                continue

            # Assuming 'content' is the field to be chunked and vectorized
            content = post.content
            chunks = self.chunk_content(content)  # Chunk content into 2-3 sentence chunks

            for chunk_text in chunks:
                # Vectorize chunk
                chunk_vector = self.vectorize_text(chunk_text, tokenizer, model)
                # Create and save chunk instance
                Chunk.objects.create(
                    post=post,
                    chunk_text=chunk_text,
                    chunk_vector=chunk_vector
                )

            self.stdout.write(self.style.SUCCESS(f'Processed post {post.id}'))

    def chunk_content(self, content):
        """
        Splits the content into chunks of 2-3 sentences.
        """
        sentences = sent_tokenize(content)
        chunks = []

        # Group sentences into chunks of 2-3
        for i in range(0, len(sentences), 3):  # Adjust this for different chunk sizes
            chunk = " ".join(sentences[i:i+3])
            chunks.append(chunk)

        return chunks

    def vectorize_text(self, text, tokenizer, model):
        """
        Vectorizes the given text using the specified tokenizer and model.
        """
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        vector = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()  # Example vectorization strategy
        return vector
