from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import tempfile
import os
from .models import (
    QuestionRequest, 
    AnswerResponse, 
    DocumentUpload,
    SearchResponse,
    KnowledgeBaseStats
)
from .knowledge_base import KnowledgeBase, DocumentProcessor
from .nlp_engine import NLPEngine, AnswerGenerator

router = APIRouter()

# Initialize components
kb = KnowledgeBase()
nlp_engine = NLPEngine()
answer_generator = AnswerGenerator(nlp_engine)

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(question_request: QuestionRequest):
    """Ask a question and get an answer"""
    try:
        # Search for similar questions in knowledge base
        similar_qa = kb.find_similar_questions(question_request.question)
        
        if similar_qa and similar_qa[0]['confidence_score'] > 0.8:
            # Return existing high-confidence answer
            best_match = similar_qa[0]
            return AnswerResponse(
                answer=best_match['answer'],
                confidence=best_match['confidence_score'],
                confidence_level="high",
                source_documents=[],
                related_questions=[qa['question'] for qa in similar_qa[1:4]],
                processing_time=0.1
            )
        
        # Search for relevant documents
        relevant_docs = kb.search_documents(
            question_request.question, 
            limit=question_request.max_results
        )
        
        # Extract document content for NLP processing
        doc_contents = [doc['content'] for doc in relevant_docs]
        nlp_engine.add_documents(doc_contents)
        
        # Generate answer
        result = answer_generator.generate_answer(
            question_request.question, 
            doc_contents
        )
        
        return AnswerResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            confidence_level="high" if result["confidence"] > 0.7 else "medium",
            source_documents=relevant_docs,
            related_questions=result["keywords"],
            processing_time=0.5
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.post("/documents", status_code=201)
async def add_document(document: DocumentUpload):
    """Add a document to the knowledge base"""
    try:
        document_id = kb.add_document(
            title=document.title,
            content=document.content,
            category=document.category,
            tags=document.tags
        )
        
        # Add QA pairs if provided in content
        # This is a simplified example - in reality, you'd extract QA pairs
        if "?" in document.content:
            # Simple QA extraction logic
            sentences = document.content.split('.')
            for sentence in sentences:
                if "?" in sentence:
                    # This is overly simplified - use proper NLP in production
                    parts = sentence.split('?')
                    if len(parts) >= 2:
                        question = parts[0] + "?"
                        answer = parts[1].strip()
                        if len(question) > 10 and len(answer) > 5:
                            kb.add_qa_pair(question, answer, document_id)
        
        return {"document_id": document_id, "message": "Document added successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    tags: str = Form("")
):
    """Upload a document file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process the document
        processor = DocumentProcessor(kb)
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        document_id = processor.process_document_file(tmp_path, category, tag_list)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return {"document_id": document_id, "message": "File uploaded and processed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/search")
async def search_documents(query: str, category: Optional[str] = None, limit: int = 10) -> SearchResponse:
    """Search documents in the knowledge base"""
    try:
        results = kb.search_documents(query, category, limit)
        
        return SearchResponse(
            query=query,
            results=results,
            total_count=len(results),
            processing_time=0.2
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/stats", response_model=KnowledgeBaseStats)
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        with kb.conn:
            cursor = kb.conn.cursor()
            
            # Get total documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]
            
            # Get total QA pairs
            cursor.execute("SELECT COUNT(*) FROM questions_answers")
            total_qa = cursor.fetchone()[0]
            
            # Get categories count
            cursor.execute("SELECT category, COUNT(*) FROM documents GROUP BY category")
            categories = {row[0] or 'Uncategorized': row[1] for row in cursor.fetchall()}
            
            # Get last updated timestamp
            cursor.execute("SELECT MAX(updated_at) FROM documents")
            last_updated = cursor.fetchone()[0]
            
            return KnowledgeBaseStats(
                total_documents=total_docs,
                total_qa_pairs=total_qa,
                categories=categories,
                last_updated=last_updated
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document from the knowledge base"""
    try:
        with kb.conn:
            cursor = kb.conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Document not found")
            
            return {"message": "Document deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")