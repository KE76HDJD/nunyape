import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger('qa-knowledge-base')

class KnowledgeBase:
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the knowledge base database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS questions_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    document_id INTEGER,
                    confidence_score REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    embedding_vector BLOB,
                    model_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
    
    def add_document(self, title: str, content: str, category: str = None, tags: List[str] = None):
        """Add a document to the knowledge base"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (title, content, category, tags)
                VALUES (?, ?, ?, ?)
            ''', (title, content, category, json.dumps(tags) if tags else None))
            
            document_id = cursor.lastrowid
            logger.info(f"Added document {document_id}: {title}")
            return document_id
    
    def search_documents(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by content"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT * FROM documents 
                    WHERE (title LIKE ? OR content LIKE ?) AND category = ?
                    ORDER BY updated_at DESC LIMIT ?
                ''', (f'%{query}%', f'%{query}%', category, limit))
            else:
                cursor.execute('''
                    SELECT * FROM documents 
                    WHERE title LIKE ? OR content LIKE ?
                    ORDER BY updated_at DESC LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            # Parse tags from JSON
            for result in results:
                if result['tags']:
                    result['tags'] = json.loads(result['tags'])
            
            return results
    
    def add_qa_pair(self, question: str, answer: str, document_id: Optional[int] = None, confidence: float = 1.0):
        """Add a question-answer pair"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO questions_answers (question, answer, document_id, confidence_score)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, document_id, confidence))
            
            qa_id = cursor.lastrowid
            logger.info(f"Added QA pair {qa_id}")
            return qa_id
    
    def find_similar_questions(self, question: str, threshold: float = 0.7, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar questions in the knowledge base"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Simple similarity search (in production, use embeddings)
            cursor.execute('''
                SELECT *, 
                       (LENGTH(?) - LENGTH(REPLACE(LOWER(?), LOWER(question), ''))) / LENGTH(question) AS similarity
                FROM questions_answers 
                WHERE LOWER(question) LIKE LOWER(?)
                ORDER BY similarity DESC, confidence_score DESC
                LIMIT ?
            ''', (question, question, f'%{question}%', limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            return [r for r in results if r['similarity'] >= threshold]
    
    def get_document_qa_pairs(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all QA pairs for a document"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM questions_answers 
                WHERE document_id = ?
                ORDER BY confidence_score DESC
            ''', (document_id,))
            
            return [dict(row) for row in cursor.fetchall()]

class DocumentProcessor:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.supported_formats = ['.txt', '.md', '.pdf']
    
    def process_document_file(self, file_path: str, category: str = None, tags: List[str] = None) -> int:
        """Process a document file and add to knowledge base"""
        path = Path(file_path)
        
        if path.suffix not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        try:
            if path.suffix == '.txt':
                content = path.read_text(encoding='utf-8')
            elif path.suffix == '.md':
                content = path.read_text(encoding='utf-8')
            # Add PDF processing here if needed
            
            document_id = self.kb.add_document(
                title=path.stem,
                content=content,
                category=category,
                tags=tags
            )
            
            logger.info(f"Processed document {document_id} from {file_path}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise