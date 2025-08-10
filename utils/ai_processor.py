"""
AI Processing Module
Handles OpenAI API integration for document summarization and chat
"""

import os
import openai
from typing import Optional, List, Dict
from utils.vector_processor import VectorProcessor

class AIProcessor:
    """Handles AI-powered document processing and chat functionality"""
    
    def __init__(self):
        """Initialize OpenAI client and vector processor"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Use the simplest initialization method
        openai.api_key = api_key
        
        # Initialize vector processor
        try:
            self.vector_processor = VectorProcessor()
            self.use_vector_db = True
            print("✅ Vector database initialized successfully")
        except Exception as e:
            print(f"⚠️ Vector database not available: {e}")
            self.vector_processor = None
            self.use_vector_db = False
    
    def generate_summary(self, text: str, document_id: str = None, max_tokens: int = 1000) -> str:
        """
        Generate a summary of the provided text
        
        Args:
            text: The text to summarize
            document_id: Document ID for vector storage
            max_tokens: Maximum tokens for the response
            
        Returns:
            Generated summary
        """
        try:
            # Store document in vector database if available
            if self.use_vector_db and document_id:
                metadata = {
                    'document_type': 'uploaded',
                    'summary_generated': True
                }
                self.vector_processor.store_document(document_id, text, metadata)
            
            # Truncate text if it's too long (OpenAI has token limits)
            max_input_tokens = 4000  # Conservative limit
            if len(text) > max_input_tokens:
                text = text[:max_input_tokens] + "..."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides clear, concise summaries of documents. Always be accurate and helpful."
                    },
                    {
                        "role": "user",
                        "content": f"Please provide a comprehensive summary of the following document:\n\n{text}"
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def answer_question(self, question: str, document_text: str = None, document_id: str = None, max_tokens: int = 1000) -> str:
        """
        Answer a question based on the document content using vector search
        
        Args:
            question: The user's question
            document_text: The document text to reference (fallback)
            document_id: Document ID for vector search
            max_tokens: Maximum tokens for the response
            
        Returns:
            AI-generated answer
        """
        try:
            context_text = ""
            
            # Use vector search if available
            if self.use_vector_db and document_id:
                # Search for relevant chunks
                similar_chunks = self.vector_processor.search_similar_chunks(question, document_id, top_k=3)
                
                if similar_chunks:
                    # Combine relevant chunks
                    context_text = "\n\n".join([chunk['text'] for chunk in similar_chunks])
                    print(f"Found {len(similar_chunks)} relevant chunks from vector search")
                else:
                    # Fallback to full document text
                    if document_text:
                        context_text = document_text
                        print("No relevant chunks found, using full document")
            else:
                # Use provided document text
                context_text = document_text or ""
                print("Using provided document text")
            
            if not context_text:
                return "I don't have enough context to answer this question. Please upload a document first."
            
            # Truncate text if it's too long
            max_input_tokens = 4000
            if len(context_text) > max_input_tokens:
                context_text = context_text[:max_input_tokens] + "..."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions about documents. Always be accurate and helpful based on the document content. If the information is not in the provided context, say so."
                    },
                    {
                        "role": "user",
                        "content": f"Based on the following document context, answer this question: '{question}'\n\nDocument Context:\n{context_text}"
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error answering question: {str(e)}")
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search across all documents in the vector database
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.use_vector_db:
            return []
        
        try:
            results = self.vector_processor.search_similar_chunks(query, top_k=top_k)
            return results
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[Dict]:
        """
        Get all chunks for a specific document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of document chunks
        """
        if not self.use_vector_db:
            return []
        
        try:
            return self.vector_processor.get_document_chunks(document_id)
        except Exception as e:
            print(f"Error getting document chunks: {str(e)}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector database
        
        Args:
            document_id: Document ID
            
        Returns:
            Success status
        """
        if not self.use_vector_db:
            return False
        
        try:
            return self.vector_processor.delete_document(document_id)
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False
    
    def get_vector_stats(self) -> Dict:
        """
        Get vector database statistics
        
        Returns:
            Dictionary with vector database stats
        """
        if not self.use_vector_db:
            return {'vector_db_available': False}
        
        try:
            stats = self.vector_processor.get_index_stats()
            stats['vector_db_available'] = True
            return stats
        except Exception as e:
            print(f"Error getting vector stats: {str(e)}")
            return {'vector_db_available': False}
    
    def validate_api_key(self) -> bool:
        """Validate that the OpenAI API key is working"""
        try:
            # Make a simple test call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False 