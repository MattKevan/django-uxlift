from django.core.management.base import BaseCommand
from apps.content.models import Post  # Assuming your model is named Post and is in an app named content
from llama_index.core import Document
import chromadb
from llama_index.core import StorageContext, VectorStoreIndex, SimpleDirectoryReader, Settings, ServiceContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.readers.file import CSVReader
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import TokenTextSplitter

class Command(BaseCommand):
    help = 'Indexes all posts in the database with LlamaIndex'

    def handle(self, *args, **options):
        posts = Post.objects.filter(indexed=False)  # Retrieve all posts
        documents = []

        for post in posts:
            # Skip posts where content is None
            if post.content is None:
                self.stdout.write(self.style.WARNING(f'Skipping post {post.id} due to empty content'))
                continue
            
            # Construct document with post content and metadata
            document = Document(
                text=post.content,  # Use the post's content as the main text
                metadata={
                    "title": post.title,
                    "id": str(post.id),  # Ensure ID is a string
                    "date_published": post.date_published.isoformat(),
                    "link": post.link  # Assuming your Post model has a 'link' field
                }
            )
            documents.append(document)
            post.indexed = True
            post.save()

        db = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = db.get_or_create_collection("uxlift")
        
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )

        # Print the first document to verify
        for doc in documents[:1]:
            self.stdout.write(f"Document Text: {doc.text}")
            self.stdout.write(f"Metadata: {doc.metadata}")
            self.stdout.write("\n" + "-"*40 + "\n")  # Separator for readability

        self.stdout.write(self.style.SUCCESS(f'Successfully indexed {len(documents)} posts.'))
