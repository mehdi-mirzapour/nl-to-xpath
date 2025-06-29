import os
import asyncio
from dotenv import load_dotenv
from langchain_mistralai import MistralAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document

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
    print("Warning: HF_TOKEN not set. Set it to avoid dummy tokenizer.")

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

def chunk_raw_html(html_content, max_chunk_size=300):
    """Chunk raw HTML content into documents with metadata."""
    return [
        Document(
            page_content=html_content[i:i + max_chunk_size],
            metadata={
                'source': 'raw_html',
                'original_html': html_content,
                'start_offset': i,
                'end_offset': min(i + max_chunk_size, len(html_content))
            }
        ) for i in range(0, len(html_content), max_chunk_size)
    ]

async def process_raw_html_for_rag(html_content):
    """Process raw HTML for RAG using async operations."""
    # Chunk the HTML content
    documents = chunk_raw_html(html_content)
    print(f"Created {len(documents)} chunks")

    # Batch embed and store in Pinecone
    try:
        vector_ids = await vector_store.aadd_documents(documents)  # Async add
        print(f"Stored {len(vector_ids)} vectors")
        return vector_ids
    except Exception as e:
        print(f"Error storing vectors: {e}")
        return []

async def query_rag(query, top_k=5):
    """Query the RAG system with a text query."""
    # Perform similarity search
    results = await vector_store.asimilarity_search_with_score(query, k=top_k)
    
    # Format results
    return [
        {
            'text': doc.page_content,
            'start_offset': doc.metadata['start_offset'],
            'end_offset': doc.metadata['end_offset'],
            'score': score
        } for doc, score in results
    ]

# Example usage with async
async def main():
    sample_html = """
    <html>
        <head><title>Company Website</title></head>
        <body>
            <h1>Welcome to Horizon Innovations</h1>
            <p>We provide cutting-edge AI solutions and consulting services to empower businesses.</p>
            <div class="services">
                <h2>Our Services</h2>
                <ul>
                    <li>AI Model Development</li>
                    <li>Data Analytics</li>
                    <li>Cloud Integration</li>
                </ul>
            </div>
            <div class="contact">
                <h2>Contact Us</h2>
                <p>Email: info@horizon.com</p>
                <p>Phone: (123) 456-7890</p>
                <p>Address: 123 Innovation Drive, Tech City</p>
            </div>
            <footer>
                <p>© 2025 Horizon Innovations. All rights reserved.</p>
            </footer>
        </body>
    </html>
    """
    
    # Process raw HTML
    vector_ids = await process_raw_html_for_rag(sample_html)
    print(f"Stored vectors with IDs: {vector_ids}")
    
    # Example query
    query = "What is the contact email for Horizon Innovations?"
    results = await query_rag(query)
    print("\nQuery results:")
    for result in results:
        print(f"Chunk: {result['text']}")
        print(f"Offsets: {result['start_offset']} - {result['end_offset']}")
        print(f"Score: {result['score']}\n")

if __name__ == "__main__":
    asyncio.run(main())