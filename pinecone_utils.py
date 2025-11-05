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

    def format_citation(self, doc: Dict, index: int) -> str:
        """
        Format a citation with PDF link that opens to specific page

        Expected metadata fields:
        - source or filename: PDF filename or path
        - page or page_number: Page number (int)
        - pdf_url or path: URL or path to PDF file
        - title: Optional document title
        """
        metadata = doc.get("metadata", {})

        # Support both 'source' and 'filename' fields
        source = metadata.get("source") or metadata.get("filename", "Unknown Source")

        # Support both 'page' and 'page_number' fields
        page = metadata.get("page") or metadata.get("page_number", 1)

        # Convert page to int if it's a float
        if isinstance(page, float):
            page = int(page)

        # Get PDF URL - check pdf_url first, then construct from path or use base URL
        pdf_url = metadata.get("pdf_url", "")

        # If no pdf_url but we have a path, try to construct URL
        if not pdf_url and metadata.get("path"):
            path = metadata.get("path")
            # If BASE_PDF_URL is set in environment, use it to construct full URL
            base_url = os.getenv("BASE_PDF_URL", "")
            if base_url:
                # Remove 'pdfs/' prefix if it exists in path
                filename = path.replace("pdfs/", "")
                pdf_url = f"{base_url.rstrip('/')}/{filename}"

        # Use title if available, otherwise use source/filename
        title = metadata.get("title", source)

        # Create PDF link with page anchor
        # PDF links use #page=N to jump to specific page
        if pdf_url:
            citation_link = f"{pdf_url}#page={page}"
            citation = f"[{title}, p.{page}]({citation_link})"
        else:
            citation = f"{title}, p.{page}"

        return citation