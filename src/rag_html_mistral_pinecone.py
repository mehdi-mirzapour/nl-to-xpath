import os
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
max_token_limitation = int(os.getenv("MAX_TOKEN_LIMITATION", 12000))  # Default to 12000 if not set

# Validate environment variables
if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not set in environment.")
if not pinecone_api_key:
    raise ValueError("PINECONE_API_KEY not set in environment.")

def initialize_pinecone(index_name, dimension=1024, metric="cosine", cloud="aws", region="us-east-1", namespace="default"):
    if not pinecone_api_key:
        raise ValueError("Pinecone API key is not provided.")

    try:
        pc = Pinecone(api_key=pinecone_api_key)
    except Exception as e:
        raise ConnectionError(f"Failed to initialize Pinecone client: {e}")

    if index_name in pc.list_indexes().names():
        index = pc.Index(index_name)
        
        # Check index configuration
        index_desc = pc.describe_index(index_name)
        if index_desc.dimension != dimension or index_desc.metric != metric:
            raise RuntimeError(
                f"Existing index '{index_name}' has dimension={index_desc.dimension} and metric={index_desc.metric}, "
                f"but requested dimension={dimension} and metric={metric}."
            )

        # Check if namespace is empty
        try:
            stats = index.describe_index_stats()
            namespace_stats = stats.get("namespaces", {}).get(namespace, {})
            vector_count = namespace_stats.get("vector_count", 0)

            if vector_count > 0:
                print(f"Namespace '{namespace}' has {vector_count} vectors — deleting...")
                index.delete(delete_all=True, namespace=namespace)
            else:
                print(f"Namespace '{namespace}' is already empty. No delete needed.")
        except Exception as e:
            raise RuntimeError(f"Failed to check or clear vectors in index '{index_name}': {e}")
    else:
        try:
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud=cloud, region=region)
            )
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(1)
        except Exception as e:
            raise RuntimeError(f"Failed to create index '{index_name}': {e}")

    return pc.Index(index_name)

# Chunk HTML at character level
def chunk_html(html_content, chunk_size):
    chunks = []
    for i in range(0, len(html_content), chunk_size):
        chunk = html_content[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

# Find most similar chunk
def find_similar_chunk(html_content, query, chunk_size= max_token_limitation, index_name="default-index"):
    # Set Mistral AI embedding model (calls Mistral API)
    Settings.embed_model = MistralAIEmbedding(
        model_name="mistral-embed",
        api_key=mistral_api_key
    )
    
    # Disable LLM since it's not needed for similarity search
    Settings.llm = None
  
    
    # Initialize Pinecone
    pinecone_index = initialize_pinecone(index_name)
    
    # Create vector store
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # Chunk the HTML
    chunks = chunk_html(html_content, chunk_size)
    
    # Create documents from chunks
    documents = [Document(text=chunk, metadata={"chunk_index": i}) for i, chunk in enumerate(chunks)]
    
    # Create index
    index = VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        show_progress=True
    )
    
    # Query the index
    query_engine = index.as_query_engine(similarity_top_k=1)
    response = query_engine.query(query)
    
    # Get the most similar chunk
    if response.source_nodes:
        best_chunk = response.source_nodes[0].text
        chunk_index = response.source_nodes[0].metadata["chunk_index"]
        similarity_score = response.source_nodes[0].score
    else: 
        best_chunk = ""
        chunk_index = -1
        similarity_score = 0.0
    
    return {
        "total_chunks": len(chunks),
        "selected_chunk_index": chunk_index,
        "selected_chunk": best_chunk,
        "similarity_score": similarity_score
    }

# Main function to process HTML and query
def process_html_query(html_content, query, chunk_size=max_token_limitation, index_name=os.getenv("PINECONE_INDEX_NAME")
):
    result = find_similar_chunk(html_content, query, chunk_size, index_name)
    
    output = f"""Number of chunks created: {result['total_chunks']}
Selected chunk index: {result['selected_chunk_index']}
Similarity score: {result['similarity_score']:.4f}
Selected chunk content:
{result['selected_chunk']}"""
    
    return output

# Example usage
if __name__ == "__main__":
    # Example inputs
    html_content = "<html><body><h1>Example HTML</h1><p>This is a very long HTML content...</p></body></html>"  # Replace with your HTML
    chunk_size = 12000
    query = "example query text"

    # Process and print results
    result = process_html_query(html_content, query)
    print(result)