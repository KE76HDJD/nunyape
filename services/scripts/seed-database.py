#!/usr/bin/env python3

"""
Database seeding script for development environment
"""

import os
import sys
import psycopg2
from psycopg2.extras import execute_values
import json
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'appdb'),
        user=os.getenv('DB_USER', 'appuser'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

def seed_users(conn):
    """Seed users table"""
    users = [
        {
            'id': 'user_1',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password_hash': 'hashed_password_123',  # In real app, use proper hashing
            'role': 'admin',
            'is_active': True
        },
        {
            'id': 'user_2',
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password_hash': 'hashed_password_456',
            'role': 'user',
            'is_active': True
        },
        {
            'id': 'user_3',
            'email': 'jane.smith@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password_hash': 'hashed_password_789',
            'role': 'user',
            'is_active': True
        }
    ]
    
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO users (id, email, first_name, last_name, password_hash, role, is_active, created_at, updated_at)
            VALUES %s
            ON CONFLICT (id) DO NOTHING
            """,
            [
                (
                    user['id'],
                    user['email'],
                    user['first_name'],
                    user['last_name'],
                    user['password_hash'],
                    user['role'],
                    user['is_active'],
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                for user in users
            ]
        )
    
    print(f"Seeded {len(users)} users")

def seed_presentations(conn):
    """Seed presentations table"""
    presentations = [
        {
            'id': 'pres_1',
            'title': 'Introduction to Microservices',
            'description': 'A comprehensive introduction to microservices architecture',
            'owner_id': 'user_1',
            'status': 'published',
            'theme': 'modern'
        },
        {
            'id': 'pres_2',
            'title': 'API Design Best Practices',
            'description': 'Learn the best practices for designing RESTful APIs',
            'owner_id': 'user_2',
            'status': 'draft',
            'theme': 'classic'
        },
        {
            'id': 'pres_3',
            'title': 'Cloud Native Applications',
            'description': 'Building applications for the cloud era',
            'owner_id': 'user_1',
            'status': 'published',
            'theme': 'dark'
        }
    ]
    
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO presentations (id, title, description, owner_id, status, theme, created_at, updated_at)
            VALUES %s
            ON CONFLICT (id) DO NOTHING
            """,
            [
                (
                    pres['id'],
                    pres['title'],
                    pres['description'],
                    pres['owner_id'],
                    pres['status'],
                    pres['theme'],
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                for pres in presentations
            ]
        )
    
    print(f"Seeded {len(presentations)} presentations")

def seed_qa_knowledge_base(conn):
    """Seed Q&A knowledge base"""
    documents = [
        {
            'title': 'Microservices Architecture Guide',
            'content': '''
                Microservices architecture is a method of developing software systems 
                that tries to focus on building single-function modules with well-defined 
                interfaces and operations. These modules can be deployed independently 
                and communicate with each other using lightweight protocols.
                
                What are the benefits of microservices?
                Microservices offer several benefits including independent deployability, 
                technology diversity, fault isolation, and scalability.
                
                How to implement microservices?
                To implement microservices, you need to: 1) Identify business capabilities, 
                2) Define service boundaries, 3) Implement APIs, 4) Set up infrastructure.
            ''',
            'category': 'architecture'
        },
        {
            'title': 'API Design Principles',
            'content': '''
                RESTful API design follows several key principles: 
                1. Use HTTP methods explicitly
                2. Be stateless
                3. Use URI to represent resources
                4. Handle errors gracefully
                5. Support content negotiation
                
                What is REST?
                REST stands for Representational State Transfer. It is an architectural style 
                for designing networked applications.
                
                How to handle authentication in APIs?
                Common methods include API keys, JWT tokens, and OAuth 2.0.
            ''',
            'category': 'api-design'
        }
    ]
    
    with conn.cursor() as cur:
        for doc in documents:
            cur.execute(
                """
                INSERT INTO documents (title, content, category, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (doc['title'], doc['content'], doc['category'], datetime.utcnow(), datetime.utcnow())
            )
            
            doc_id = cur.fetchone()[0]
            
            # Add some QA pairs
            qa_pairs = [
                ('What are microservices?', 'Microservices are an architectural style that structures an application as a collection of loosely coupled services.', doc_id),
                ('What are the benefits of microservices?', 'Benefits include independent deployability, technology diversity, fault isolation, and scalability.', doc_id),
                ('What is REST?', 'REST stands for Representational State Transfer, an architectural style for designing networked applications.', doc_id)
            ]
            
            for question, answer, doc_id in qa_pairs:
                cur.execute(
                    """
                    INSERT INTO questions_answers (question, answer, document_id, confidence_score, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (question, answer, doc_id, 0.9, datetime.utcnow())
                )
    
    print("Seeded Q&A knowledge base with documents and questions")

def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    try:
        conn = get_db_connection()
        
        # Seed tables
        seed_users(conn)
        seed_presentations(conn)
        seed_qa_knowledge_base(conn)
        
        # Commit changes
        conn.commit()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()