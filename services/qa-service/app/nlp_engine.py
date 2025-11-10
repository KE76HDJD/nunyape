import re
import string
from typing import List, Dict, Any, Tuple
import logging
from collections import Counter
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger('qa-nlp-engine')

class NLPEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        self.documents = []
        self.document_vectors = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, using simple tokenization")
            self.nlp = None
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for NLP tasks"""
        if self.nlp:
            doc = self.nlp(text.lower())
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            return ' '.join(tokens)
        else:
            # Simple preprocessing without spaCy
            text = text.lower()
            text = re.sub(f'[{string.punctuation}]', ' ', text)
            tokens = text.split()
            return ' '.join(tokens)
    
    def add_documents(self, documents: List[str]):
        """Add documents to the NLP engine"""
        self.documents.extend(documents)
        if self.documents:
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
    
    def find_similar_documents(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Find documents similar to the query"""
        if not self.documents or self.document_vectors is None:
            return []
        
        query_processed = self.preprocess_text(query)
        query_vector = self.vectorizer.transform([query_processed])
        
        similarities = cosine_similarity(query_vector, self.document_vectors)
        similar_indices = similarities.argsort()[0][-top_k:][::-1]
        
        results = []
        for idx in similar_indices:
            if similarities[0, idx] > 0.1:  # Minimum similarity threshold
                results.append((idx, similarities[0, idx]))
        
        return results
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text"""
        processed_text = self.preprocess_text(text)
        
        if self.nlp:
            doc = self.nlp(processed_text)
            # Extract nouns and proper nouns
            keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
        else:
            keywords = processed_text.split()
        
        # Get most common keywords
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(top_n)]
    
    def classify_question_type(self, question: str) -> str:
        """Classify the type of question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['how to', 'how do i', 'steps to', 'procedure']):
            return "procedural"
        elif any(word in question_lower for word in ['what is', 'what are', 'define', 'meaning of']):
            return "conceptual"
        elif any(word in question_lower for word in ['compare', 'difference between', 'vs', 'versus']):
            return "comparative"
        else:
            return "factual"

class AnswerGenerator:
    def __init__(self, nlp_engine: NLPEngine):
        self.nlp = nlp_engine
    
    def generate_answer(self, question: str, context_documents: List[str]) -> Dict[str, Any]:
        """Generate an answer based on question and context"""
        question_type = self.nlp.classify_question_type(question)
        
        # Simple answer generation logic
        if question_type == "factual":
            answer = self._generate_factual_answer(question, context_documents)
        elif question_type == "procedural":
            answer = self._generate_procedural_answer(question, context_documents)
        elif question_type == "conceptual":
            answer = self._generate_conceptual_answer(question, context_documents)
        else:
            answer = self._generate_comparative_answer(question, context_documents)
        
        # Calculate confidence based on answer quality and context relevance
        confidence = self._calculate_confidence(answer, context_documents)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "question_type": question_type,
            "keywords": self.nlp.extract_keywords(question)
        }
    
    def _generate_factual_answer(self, question: str, context_documents: List[str]) -> str:
        """Generate factual answers"""
        # Simple extraction-based answering
        for doc in context_documents:
            if any(self.nlp.preprocess_text(question) in self.nlp.preprocess_text(doc) for word in question.split()):
                # Return the most relevant sentence
                sentences = doc.split('.')
                for sentence in sentences:
                    if any(word in sentence.lower() for word in question.lower().split()):
                        return sentence.strip()
        
        return "I couldn't find a specific answer to your question in the available documents."
    
    def _generate_procedural_answer(self, question: str, context_documents: List[str]) -> str:
        """Generate procedural answers"""
        return f"Based on the available information, here are the general steps: [Procedural steps would be extracted from context documents]"
    
    def _generate_conceptual_answer(self, question: str, context_documents: List[str]) -> str:
        """Generate conceptual answers"""
        return f"Based on the documentation, this concept can be defined as: [Concept definition would be extracted from context documents]"
    
    def _generate_comparative_answer(self, question: str, context_documents: List[str]) -> str:
        """Generate comparative answers"""
        return f"Based on the available information, here's a comparison: [Comparative analysis would be extracted from context documents]"
    
    def _calculate_confidence(self, answer: str, context_documents: List[str]) -> float:
        """Calculate confidence score for the generated answer"""
        if not context_documents:
            return 0.1
        
        # Simple confidence calculation based on answer length and context relevance
        base_confidence = min(len(answer) / 100, 1.0)
        context_relevance = min(len(context_documents) / 5, 1.0)
        
        return round(base_confidence * context_relevance, 2)