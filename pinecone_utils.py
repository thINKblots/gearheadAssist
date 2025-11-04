from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict


class PineconeRAG:
    def __init__(self, index_name: str = None):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")

        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "gearhead-docs")

        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        try:
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            print(f"Error connecting to index: {e}")
            self.index = None
    
    def create_index_if_not_exists(self, dimension: int = 384):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            self.index = self.pc.Index(self.index_name)
    
    def embed_text(self, text: str) -> List[float]:
        return self.embedding_model.encode(text).tolist()
    
    def upsert_documents(self, documents: List[Dict[str, str]]):
        """
        Upload documents to Pinecone
        documents format: [
        {"id": "doc1", "text": "content here", "metadata": {"source": "manual.pdf"}}]
        """
        if not self.index:
            raise Exception("Index not initialized")
        
        vectors = []
        for doc in documents:
            vector_id = doc["id"]
            text = doc["text"]
            metadata = doc.get("metadata", {})
            metadata["text"] = text
            embedding = self.embed_text(text)

            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })

        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

    def query(self, question: str, top_k: int = 3) -> List[Dict]:
        """
        Query Pinecone for relevant documents
        Returns list of matches with text and metadata
        """
        if not self.index:
            return []
        
        query_embedding = self.embed_text(question)

        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        matches = []
        for match in results.matches:
            matches.append({
                "id": match.id,
                "score": match.score,
                "text": match.metadata.get("text", ""),
                "metadata": match.metadata
            })
        
        return matches