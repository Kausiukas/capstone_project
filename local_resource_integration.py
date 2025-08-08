#!/usr/bin/env python3
"""
Local Resource Integration Script
Immediate implementation to leverage local PostgreSQL with pgvector and other resources
for rapid AI agent development.
"""

import os
import sys
import json
import time
import logging
import psycopg2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalResourceIntegration:
    """
    Main class for integrating local resources into the AI agent system.
    Leverages PostgreSQL with pgvector for knowledge storage and retrieval.
    """
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
        self.setup_database()
        self.discovered_resources = {}
        
    def setup_database(self):
        """Setup PostgreSQL connection and pgvector extension"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("✅ Connected to PostgreSQL database")
            
            # Setup pgvector extension
            with self.connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
                logger.info("✅ pgvector extension ready")
                
                # Create knowledge embeddings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        embedding vector(1536),
                        source_type VARCHAR(50),
                        source_path TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create code patterns table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS code_patterns (
                        id SERIAL PRIMARY KEY,
                        pattern_name VARCHAR(100),
                        pattern_code TEXT,
                        pattern_type VARCHAR(50),
                        source_file TEXT,
                        complexity_score FLOAT,
                        usefulness_score FLOAT,
                        embedding vector(1536),
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create learning goals table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_goals (
                        id SERIAL PRIMARY KEY,
                        goal_description TEXT NOT NULL,
                        goal_type VARCHAR(50),
                        priority VARCHAR(20),
                        status VARCHAR(20) DEFAULT 'active',
                        source_resource TEXT,
                        progress_data JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create personality traits table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS personality_traits (
                        id SERIAL PRIMARY KEY,
                        trait_name VARCHAR(50),
                        trait_value FLOAT,
                        confidence FLOAT,
                        source_pattern TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
            self.connection.commit()
            logger.info("✅ Database tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
    
    def discover_local_resources(self, base_directories: List[str] = None):
        """Discover useful resources from local directories"""
        if base_directories is None:
            base_directories = [
                "D:/GUI/System-Reference-Clean/",
                "./src/",
                "./docs/",
                "./scripts/",
                "./tests/",
                "./web/"
            ]
        
        logger.info("🔍 Starting local resource discovery...")
        
        discovered = {
            'code_files': [],
            'documents': [],
            'prototypes': [],
            'configurations': [],
            'datasets': []
        }
        
        for directory in base_directories:
            if os.path.exists(directory):
                logger.info(f"📁 Scanning directory: {directory}")
                discovered['code_files'].extend(self.discover_code_files(directory))
                discovered['documents'].extend(self.discover_documents(directory))
                discovered['prototypes'].extend(self.discover_prototypes(directory))
                discovered['configurations'].extend(self.discover_configurations(directory))
        
        self.discovered_resources = discovered
        logger.info(f"✅ Discovered {sum(len(v) for v in discovered.values())} resources")
        return discovered
    
    def discover_code_files(self, directory: str) -> List[Dict]:
        """Discover and analyze code files"""
        code_files = []
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp'}
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix in code_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        analysis = self.analyze_code_file(file_path)
                        if analysis['usefulness_score'] > 0.3:  # Threshold for useful code
                            code_files.append({
                                'path': file_path,
                                'analysis': analysis,
                                'size': os.path.getsize(file_path),
                                'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                            })
                    except Exception as e:
                        logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return code_files
    
    def discover_prototypes(self, directory: str) -> List[Dict]:
        """Discover AI agent prototypes and experimental code"""
        prototypes = []
        ai_keywords = [
            'agent', 'ai', 'llm', 'gpt', 'openai', 'anthropic', 'claude',
            'chatbot', 'assistant', 'intelligence', 'reasoning', 'memory',
            'learning', 'neural', 'transformer', 'embedding', 'vector'
        ]
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            found_keywords = [k for k in ai_keywords if k in content]
                            
                            if found_keywords:
                                prototypes.append({
                                    'path': file_path,
                                    'type': 'ai_prototype',
                                    'keywords_found': found_keywords,
                                    'relevance_score': len(found_keywords) / len(ai_keywords)
                                })
                    except Exception as e:
                        logger.warning(f"Failed to read {file_path}: {e}")
        
        return prototypes
    
    def discover_documents(self, directory: str) -> List[Dict]:
        """Discover documentation and knowledge files"""
        documents = []
        doc_extensions = {'.md', '.txt', '.rst', '.docx', '.pdf', '.html'}
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix in doc_extensions:
                    file_path = os.path.join(root, file)
                    documents.append({
                        'path': file_path,
                        'type': 'document',
                        'extension': Path(file).suffix,
                        'size': os.path.getsize(file_path)
                    })
        
        return documents
    
    def discover_configurations(self, directory: str) -> List[Dict]:
        """Discover configuration files"""
        config_files = []
        config_patterns = ['config', 'settings', 'env', 'yaml', 'yml', 'json', 'ini', 'toml']
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(pattern in file.lower() for pattern in config_patterns):
                    file_path = os.path.join(root, file)
                    config_files.append({
                        'path': file_path,
                        'type': 'configuration',
                        'pattern_matched': [p for p in config_patterns if p in file.lower()]
                    })
        
        return config_files
    
    def analyze_code_file(self, file_path: str) -> Dict:
        """Analyze a code file for patterns and usefulness"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'lines_of_code': len(content.splitlines()),
                'complexity_score': self.calculate_complexity(content),
                'usefulness_score': self.calculate_usefulness(content),
                'patterns': self.extract_patterns(content),
                'functions': self.extract_functions(content),
                'classes': self.extract_classes(content),
                'imports': self.extract_imports(content)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return {'usefulness_score': 0}
    
    def calculate_complexity(self, content: str) -> float:
        """Calculate code complexity score"""
        # Simple complexity metrics
        lines = content.splitlines()
        if not lines:
            return 0.0
        
        # Count various complexity indicators
        complexity_indicators = {
            'nested_blocks': len(re.findall(r'if.*:|for.*:|while.*:|try.*:', content)),
            'function_definitions': len(re.findall(r'def\s+\w+', content)),
            'class_definitions': len(re.findall(r'class\s+\w+', content)),
            'imports': len(re.findall(r'import\s+|from\s+', content)),
            'comments': len(re.findall(r'#.*$', content, re.MULTILINE))
        }
        
        # Calculate complexity score (0-1)
        total_indicators = sum(complexity_indicators.values())
        max_expected = len(lines) * 0.3  # Reasonable maximum
        
        return min(total_indicators / max_expected, 1.0) if max_expected > 0 else 0.0
    
    def calculate_usefulness(self, content: str) -> float:
        """Calculate code usefulness score"""
        usefulness_indicators = {
            'has_functions': len(re.findall(r'def\s+\w+', content)) > 0,
            'has_classes': len(re.findall(r'class\s+\w+', content)) > 0,
            'has_docstrings': len(re.findall(r'""".*?"""', content, re.DOTALL)) > 0,
            'has_comments': len(re.findall(r'#.*$', content, re.MULTILINE)) > 0,
            'has_imports': len(re.findall(r'import\s+|from\s+', content)) > 0,
            'has_error_handling': len(re.findall(r'try:|except|finally', content)) > 0,
            'has_logging': len(re.findall(r'logging|logger|print', content)) > 0
        }
        
        return sum(usefulness_indicators.values()) / len(usefulness_indicators)
    
    def extract_patterns(self, content: str) -> List[str]:
        """Extract common code patterns"""
        patterns = []
        
        # Design patterns
        if re.search(r'class.*Singleton', content):
            patterns.append('singleton_pattern')
        if re.search(r'class.*Factory', content):
            patterns.append('factory_pattern')
        if re.search(r'class.*Observer', content):
            patterns.append('observer_pattern')
        
        # AI/ML patterns
        if re.search(r'openai|gpt|llm|anthropic', content, re.IGNORECASE):
            patterns.append('ai_integration')
        if re.search(r'vector|embedding|similarity', content, re.IGNORECASE):
            patterns.append('vector_operations')
        if re.search(r'async|await', content):
            patterns.append('async_programming')
        
        # Web patterns
        if re.search(r'@app\.|FastAPI|Flask', content):
            patterns.append('web_framework')
        if re.search(r'streamlit|gradio', content, re.IGNORECASE):
            patterns.append('ui_framework')
        
        return patterns
    
    def extract_functions(self, content: str) -> List[str]:
        """Extract function names"""
        functions = re.findall(r'def\s+(\w+)', content)
        return functions
    
    def extract_classes(self, content: str) -> List[str]:
        """Extract class names"""
        classes = re.findall(r'class\s+(\w+)', content)
        return classes
    
    def extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = re.findall(r'(?:import|from)\s+([^\s]+)', content)
        return imports
    
    def store_knowledge_embedding(self, content: str, source_type: str, source_path: str, metadata: Dict = None):
        """Store knowledge with vector embedding in database"""
        try:
            # Generate simple embedding (in production, use proper embedding model)
            embedding = self.generate_simple_embedding(content)
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO knowledge_embeddings (content, embedding, source_type, source_path, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (content, embedding, source_type, source_path, json.dumps(metadata or {})))
            
            self.connection.commit()
            logger.info(f"✅ Stored knowledge embedding for {source_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store knowledge embedding: {e}")
    
    def generate_simple_embedding(self, content: str) -> List[float]:
        """Generate a simple embedding vector (placeholder for proper embedding model)"""
        # This is a placeholder - in production, use OpenAI embeddings or similar
        # For now, create a simple hash-based embedding
        hash_obj = hashlib.sha256(content.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 1536-dimensional vector (matching OpenAI embeddings)
        embedding = []
        for i in range(1536):
            embedding.append(float(hash_bytes[i % len(hash_bytes)]) / 255.0)
        
        return embedding
    
    def search_similar_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for similar knowledge using vector similarity"""
        try:
            query_embedding = self.generate_simple_embedding(query)
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT content, source_type, source_path, metadata,
                           1 - (embedding <=> %s) as similarity
                    FROM knowledge_embeddings
                    ORDER BY embedding <=> %s
                    LIMIT %s
                """, (query_embedding, query_embedding, limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'content': row[0],
                        'source_type': row[1],
                        'source_path': row[2],
                        'metadata': json.loads(row[3]) if row[3] else {},
                        'similarity': float(row[4])
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"❌ Failed to search knowledge: {e}")
            return []
    
    def generate_learning_goals(self) -> List[Dict]:
        """Generate learning goals based on discovered resources"""
        goals = []
        
        # Goals from code files
        for code_file in self.discovered_resources.get('code_files', []):
            if code_file['analysis']['usefulness_score'] > 0.7:
                goals.append({
                    'description': f"Learn advanced patterns from {os.path.basename(code_file['path'])}",
                    'goal_type': 'learning',
                    'priority': 'high',
                    'source_resource': code_file['path'],
                    'target_score': code_file['analysis']['usefulness_score']
                })
        
        # Goals from prototypes
        for prototype in self.discovered_resources.get('prototypes', []):
            if prototype['relevance_score'] > 0.5:
                goals.append({
                    'description': f"Study AI implementation from {os.path.basename(prototype['path'])}",
                    'goal_type': 'ai_learning',
                    'priority': 'medium',
                    'source_resource': prototype['path'],
                    'target_score': prototype['relevance_score']
                })
        
        return goals
    
    def store_learning_goals(self, goals: List[Dict]):
        """Store learning goals in database"""
        try:
            with self.connection.cursor() as cursor:
                for goal in goals:
                    cursor.execute("""
                        INSERT INTO learning_goals (goal_description, goal_type, priority, source_resource, progress_data)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        goal['description'],
                        goal['goal_type'],
                        goal['priority'],
                        goal['source_resource'],
                        json.dumps({'target_score': goal.get('target_score', 0)})
                    ))
            
            self.connection.commit()
            logger.info(f"✅ Stored {len(goals)} learning goals")
            
        except Exception as e:
            logger.error(f"❌ Failed to store learning goals: {e}")
    
    def continuous_learning_cycle(self, interval_seconds: int = 3600):
        """Run continuous learning cycle"""
        logger.info("🚀 Starting continuous learning cycle...")
        
        while True:
            try:
                # 1. Discover new resources
                self.discover_local_resources()
                
                # 2. Store knowledge from discovered resources
                self.store_discovered_knowledge()
                
                # 3. Generate and store learning goals
                goals = self.generate_learning_goals()
                self.store_learning_goals(goals)
                
                # 4. Log progress
                logger.info(f"✅ Learning cycle completed. Discovered {sum(len(v) for v in self.discovered_resources.values())} resources")
                
                # Wait for next cycle
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Learning cycle failed: {e}")
                time.sleep(300)  # Wait 5 minutes before retry
    
    def store_discovered_knowledge(self):
        """Store knowledge from discovered resources"""
        # Store code patterns
        for code_file in self.discovered_resources.get('code_files', []):
            if code_file['analysis']['usefulness_score'] > 0.5:
                self.store_knowledge_embedding(
                    content=f"Code file: {code_file['path']} - Patterns: {code_file['analysis']['patterns']}",
                    source_type="code_pattern",
                    source_path=code_file['path'],
                    metadata=code_file['analysis']
                )
        
        # Store prototype knowledge
        for prototype in self.discovered_resources.get('prototypes', []):
            self.store_knowledge_embedding(
                content=f"AI Prototype: {prototype['path']} - Keywords: {prototype['keywords_found']}",
                source_type="ai_prototype",
                source_path=prototype['path'],
                metadata=prototype
            )
    
    def get_system_status(self) -> Dict:
        """Get system status and statistics"""
        try:
            with self.connection.cursor() as cursor:
                # Count knowledge embeddings
                cursor.execute("SELECT COUNT(*) FROM knowledge_embeddings")
                knowledge_count = cursor.fetchone()[0]
                
                # Count learning goals
                cursor.execute("SELECT COUNT(*) FROM learning_goals")
                goals_count = cursor.fetchone()[0]
                
                # Count active goals
                cursor.execute("SELECT COUNT(*) FROM learning_goals WHERE status = 'active'")
                active_goals = cursor.fetchone()[0]
                
                # Get recent discoveries
                cursor.execute("""
                    SELECT source_type, COUNT(*) 
                    FROM knowledge_embeddings 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY source_type
                """)
                recent_discoveries = dict(cursor.fetchall())
                
                return {
                    'total_knowledge_items': knowledge_count,
                    'total_learning_goals': goals_count,
                    'active_goals': active_goals,
                    'recent_discoveries': recent_discoveries,
                    'discovered_resources': {
                        k: len(v) for k, v in self.discovered_resources.items()
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {e}")
            return {}


def main():
    """Main function to run local resource integration"""
    
    # Database configuration (update with your local PostgreSQL settings)
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'langflow_agent',
        'user': 'postgres',
        'password': 'your_password'  # Update with your password
    }
    
    try:
        # Initialize local resource integration
        lri = LocalResourceIntegration(db_config)
        
        # Discover local resources
        discovered = lri.discover_local_resources()
        
        # Print discovery results
        print("\n🔍 Local Resource Discovery Results:")
        print("=" * 50)
        for resource_type, resources in discovered.items():
            print(f"{resource_type}: {len(resources)} items")
            if resources:
                print(f"  Examples: {[os.path.basename(r['path']) for r in resources[:3]]}")
        
        # Generate learning goals
        goals = lri.generate_learning_goals()
        print(f"\n🎯 Generated {len(goals)} learning goals")
        
        # Store goals
        lri.store_learning_goals(goals)
        
        # Get system status
        status = lri.get_system_status()
        print(f"\n📊 System Status:")
        print(f"  Total knowledge items: {status.get('total_knowledge_items', 0)}")
        print(f"  Total learning goals: {status.get('total_learning_goals', 0)}")
        print(f"  Active goals: {status.get('active_goals', 0)}")
        
        # Start continuous learning (optional)
        print("\n🚀 Starting continuous learning cycle...")
        print("Press Ctrl+C to stop")
        
        lri.continuous_learning_cycle(interval_seconds=3600)  # Run every hour
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping local resource integration...")
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
