"""
Vector Processing Module
Handles Pinecone integration for document embeddings and semantic search
"""

import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class VectorProcessor:
    """Handles vector database operations with Pinecone"""
    
    def __init__(self):
        """Initialize Pinecone and sentence transformer"""
        # Initialize Pinecone
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')
        
        if not pinecone_api_key or not pinecone_environment:
            raise ValueError("PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables are required")
        
        # Initialize Pinecone client with new API
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create index
        self.index_name = "document-chatbot"
        self._ensure_index_exists()
        
    def _ensure_index_exists(self):
        """Ensure Pinecone index exists, create if it doesn't"""
        try:
            # Try to get the index
            self.index = self.pc.Index(self.index_name)
        except Exception:
            # Index doesn't exist, create it
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # Dimension for all-MiniLM-L6-v2
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait a moment for index to be ready
            import time
            time.sleep(1)
            self.index = self.pc.Index(self.index_name)
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the end
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = max(start + 1, end - overlap)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def create_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        """
        Create embeddings for text chunks
        
        Args:
            text_chunks: List of text chunks
            
        Returns:
            List of embeddings
        """
        embeddings = self.embedding_model.encode(text_chunks)
        return embeddings.tolist()
    
    def store_document(self, document_id: str, text: str, metadata: Dict = None) -> bool:
        """
        Store document chunks in Pinecone
        
        Args:
            document_id: Unique identifier for the document
            text: Document text
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Chunk the text
            chunks = self.chunk_text(text)
            
            if not chunks:
                return False
            
            # Create embeddings
            embeddings = self.create_embeddings(chunks)
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{document_id}_chunk_{i}"
                
                vector_data = {
                    'id': vector_id,
                    'values': embedding,
                    'metadata': {
                        'document_id': document_id,
                        'chunk_index': i,
                        'text': chunk,
                        'chunk_size': len(chunk),
                        **(metadata or {})
                    }
                }
                vectors.append(vector_data)
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors)
            
            return True
            
        except Exception as e:
            print(f"Error storing document: {str(e)}")
            return False
    
    def search_similar_chunks(self, query: str, document_id: str = None, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks based on query
        
        Args:
            query: Search query
            document_id: Optional document ID to filter results
            top_k: Number of top results to return
            
        Returns:
            List of similar chunks with metadata
        """
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Prepare filter
            filter_dict = {}
            if document_id:
                filter_dict['document_id'] = document_id
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding.tolist()[0],
                filter=filter_dict,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            similar_chunks = []
            for match in results.matches:
                similar_chunks.append({
                    'text': match.metadata['text'],
                    'score': match.score,
                    'document_id': match.metadata['document_id'],
                    'chunk_index': match.metadata['chunk_index']
                })
            
            return similar_chunks
            
        except Exception as e:
            print(f"Error searching chunks: {str(e)}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[Dict]:
        """
        Get all chunks for a specific document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of document chunks
        """
        try:
            results = self.index.query(
                vector=[0] * 384,  # Dummy vector
                filter={'document_id': document_id},
                top_k=1000,  # Get all chunks
                include_metadata=True
            )
            
            chunks = []
            for match in results.matches:
                chunks.append({
                    'text': match.metadata['text'],
                    'chunk_index': match.metadata['chunk_index']
                })
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x['chunk_index'])
            return chunks
            
        except Exception as e:
            print(f"Error getting document chunks: {str(e)}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks for a specific document
        
        Args:
            document_id: Document ID
            
        Returns:
            Success status
        """
        try:
            # Get all vector IDs for this document
            results = self.index.query(
                vector=[0] * 384,  # Dummy vector
                filter={'document_id': document_id},
                top_k=1000,
                include_metadata=False
            )
            
            # Delete vectors
            vector_ids = [match.id for match in results.matches]
            if vector_ids:
                self.index.delete(ids=vector_ids)
            
            return True
            
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the vector index
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces
            }
        except Exception as e:
            print(f"Error getting index stats: {str(e)}")
            return {} 