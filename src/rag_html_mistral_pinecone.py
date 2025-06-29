import os
import asyncio
from dotenv import load_dotenv
from langchain_mistralai import MistralAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")
hf_token = os.getenv("HF_TOKEN")

# Validate environment variables
if not pinecone_api_key:
    raise ValueError("PINECONE_API_KEY not set in environment.")
if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not set in environment.")
if not index_name:
    raise ValueError("PINECONE_INDEX_NAME not set in environment.")
if not hf_token:
    print("Warning: HF_TOKEN not set. Set it to avoid dummy tokenizer. Some functionality may be limited.")

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Create or connect to a Pinecone serverless index
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1024,  # Mistral-embed model output dimension
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Initialize Mistral embeddings and Pinecone vector store
embeddings = MistralAIEmbeddings(model="mistral-embed", api_key=mistral_api_key)
vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)

async def process_and_query_html(html_content, query, top_k=1, chunk_size=1000, chunk_overlap=200):
    """Process HTML content by chunking it and query the vector store, returning the most relevant chunk with metadata."""
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )

    # Split the HTML content into chunks
    chunks = text_splitter.split_text(html_content)
    documents = [
        Document(
            page_content=chunk,
            metadata={
                'source': 'raw_html',
                'start_index': start_index,
                'end_index': start_index + len(chunk)
            }
        )
        for start_index, chunk in enumerate(chunks)
    ]

    # Store the documents in Pinecone
    try:
        await vector_store.adelete(delete_all=True)
        vector_ids = await vector_store.aadd_documents(documents)
        print(f"Stored {len(vector_ids)} vectors")
    except Exception as e:
        print(f"Error storing vectors: {e}")
        return None

    # Query the vector store
    try:
        results = await vector_store.asimilarity_search_with_score(query, k=top_k)
        if results:
            doc, score = results[0]
            # Ensure offsets are integers
            start_index = int(doc.metadata.get('start_index', 0))
            end_index = int(doc.metadata.get('end_index', len(doc.page_content)))
            return {
                'text': doc.page_content,
                'start_index': start_index,
                'end_index': end_index,
                'score': score,
                'source': doc.metadata.get('source', 'unknown')
            }
        return None
    except Exception as e:
        print(f"Error querying vectors: {e}")
        return None

# Example usage
if __name__ == "__main__":
    sample_html = (
        "<html><head><title>Company Website</title></head><body>"
        "<h1>Welcome to Horizon Innovations</h1>"
        "<p>We provide cutting-edge AI solutions and consulting services to empower businesses.</p>"
        "<div class='services'><h2>Our Services</h2><ul>"
        "<li>AI Model Development</li><li>Data Analytics</li><li>Cloud Integration</li>"
        "</ul></div>"
        "<div class='contact'><h2>Contact Us</h2>"
        "<p>Email: info@horizon.com</p><p>Phone: (123) 456-7890</p>"
        "<p>Address: 123 Innovation Drive, Tech City</p></div>"
        "<footer><p>© 2025 Horizon Innovations. All rights reserved.</p></footer>"
        "</body></html>"
    )
    
    query = "What is the contact email for Horizon Innovations?"
    result = asyncio.run(process_and_query_html(sample_html, query))
    if result:
        print("\nQuery result:")
        print(f"Chunk: {result['text'][:200]}...")  # Truncate for display
        print(f"Source: {result['source']}")
        print(f"Indices: {result['start_index']} - {result['end_index']}")
        print(f"Score: {result['score']}")
    else:
        print("No results or error occurred.")