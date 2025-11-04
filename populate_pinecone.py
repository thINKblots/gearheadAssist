from pinecone_utils import PineconeRAG
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

def load_and_chunk_documents(file_path: str):
    """Load documents and split into chunks"""
    # Read your source documents (PDFs, manuals, etc.)
    # This is a simple example with a JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Adjust based on your needs
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    documents = []
    for idx, item in enumerate(data):
        # Split text into chunks
        chunks = text_splitter.split_text(item['text'])
        
        for chunk_idx, chunk in enumerate(chunks):
            documents.append({
                "id": f"doc_{idx}_chunk_{chunk_idx}",
                "text": chunk,
                "metadata": {
                    "source": item.get('source', 'unknown'),
                    "equipment_type": item.get('equipment_type', ''),
                }
            })
    
    return documents

if __name__ == "__main__":
    # Initialize RAG
    rag = PineconeRAG()
    
    # Create index if needed
    rag.create_index_if_not_exists()
    
    # Load and upload documents
    documents = load_and_chunk_documents("data/equipment_manuals.json")
    
    print(f"Uploading {len(documents)} document chunks...")
    rag.upsert_documents(documents)
    print("Done!")