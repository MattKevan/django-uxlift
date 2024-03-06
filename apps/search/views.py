from django.shortcuts import render
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.query_engine import CitationQueryEngine  # Import the CitationQueryEngine

def search_view(request):
    search_result = ""
    source_texts = []  # List to hold texts of the source nodes
    seen_links = set()  # Track seen links to ensure uniqueness

    if request.method == "POST":
        query = request.POST.get("search_query", "")
        
        # Initialize client
        db = chromadb.PersistentClient(path="./chroma_db")

        # Get collection
        chroma_collection = db.get_or_create_collection("uxlift")

        # Assign chroma as the vector_store to the context
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Load your index from stored vectors
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

        # Create the CitationQueryEngine
        query_engine = CitationQueryEngine.from_args(
            index,
            similarity_top_k=8,
            citation_chunk_size=512,
        )
        response = query_engine.query(query)
        
        # Assuming the response text itself is what you want to display as the main search result
        search_result = response  # If the response object directly contains the result text

        # Extract text from each source node used to create the response
        for source in response.source_nodes:
            metadata_str = source.node.get_metadata_str()
            # Assuming metadata_str format is consistent with your example
            lines = metadata_str.split('\n')
            metadata = {line.split(': ')[0]: line.split(': ')[1] for line in lines if line}
            link = metadata.get("link")

            if link not in seen_links:
                seen_links.add(link)  # Mark this link as seen
                source_texts.append({
                    "title": metadata.get("title"),
                    "link": link
                })
        

    # Passing both the search result and the texts of source nodes to the template
    context = {
        "search_result": search_result,
        "source_texts": source_texts,
    }
    
    return render(request, "search/search_page.html", context)
