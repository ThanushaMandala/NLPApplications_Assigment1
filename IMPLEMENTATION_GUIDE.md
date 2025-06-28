# Implementation Guide: Academic Knowledge Graph Enhancement

## Quick Start Implementation

## 1. Database Setup

### 1.1 Install Dependencies

```bash
# Update requirements.txt
pip install neo4j==5.14.1 py2neo==2021.2.3 redis==4.6.0 celery==5.3.4 prometheus-client==0.17.1
```

### 1.2 Neo4j Database Configuration

```python
# config/database.py
from neo4j import GraphDatabase
from py2neo import Graph, Node, Relationship
import os

class Neo4jManager:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.graph = Graph(self.uri, auth=(self.user, self.password))
    
    def create_constraints_and_indexes(self):
        """Create database constraints and indexes for optimal performance"""
        with self.driver.session() as session:
            # Paper constraints and indexes
            session.run("CREATE CONSTRAINT paper_title IF NOT EXISTS FOR (p:Paper) REQUIRE p.title IS UNIQUE")
            session.run("CREATE INDEX paper_year IF NOT EXISTS FOR (p:Paper) ON (p.year)")
            session.run("CREATE INDEX paper_journal IF NOT EXISTS FOR (p:Paper) ON (p.journal)")
            
            # Author constraints and indexes
            session.run("CREATE CONSTRAINT author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE")
            session.run("CREATE INDEX author_paper_count IF NOT EXISTS FOR (a:Author) ON (a.paper_count)")
            
            # Journal constraints and indexes
            session.run("CREATE CONSTRAINT journal_name IF NOT EXISTS FOR (j:Journal) REQUIRE j.name IS UNIQUE")
            
            # Citation relationship indexes
            session.run("CREATE INDEX citation_year IF NOT EXISTS FOR ()-[r:CITES]-() ON (r.year)")
            session.run("CREATE INDEX citation_strength IF NOT EXISTS FOR ()-[r:CITES]-() ON (r.strength)")
    
    def close(self):
        self.driver.close()

# Global database instance
db = Neo4jManager()
```

### 1.3 Redis Cache Setup

```python
# cache/redis_cache.py
import redis
import json
from datetime import timedelta
import os

class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
    
    def get(self, key):
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key, value, expiry=3600):
        """Set value in cache with expiry"""
        try:
            self.redis.setex(key, expiry, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Clear all keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return False

# Global cache instance
cache = RedisCache()
```

## 2. Enhanced API Implementation

### 2.1 Updated App Configuration

```python
# app.py (updated)
from flask import Flask, render_template, request, jsonify
from config.database import db
from cache.redis_cache import cache
import time
from functools import wraps

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Performance monitoring
def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"{func.__name__} took {duration:.3f} seconds")
        return result
    return wrapper

# Cache decorator
def cache_result(expiry=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expiry)
            return result
        return wrapper
    return decorator
```

### 2.2 Enhanced Paper Addition

```python
@app.route('/api/papers', methods=['POST'])
@monitor_performance
def add_paper():
    """Add a new paper to the knowledge graph with Neo4j"""
    try:
        data = request.get_json()
        
        paper_title = data.get('title', '').strip()
        if not paper_title:
            return jsonify({'error': 'Paper title is required'}), 400
        
        with db.driver.session() as session:
            # Check if paper already exists
            result = session.run(
                "MATCH (p:Paper {title: $title}) RETURN p",
                title=paper_title
            )
            if result.single():
                return jsonify({'error': 'Paper already exists'}), 400
            
            # Create paper node
            session.run("""
                CREATE (p:Paper {
                    title: $title,
                    year: $year,
                    journal: $journal,
                    created_at: datetime()
                })
            """, title=paper_title, year=data.get('year'), journal=data.get('journal'))
            
            # Add authors
            authors = data.get('authors', [])
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(',')]
            
            for author in authors:
                if author.strip():
                    # Create or merge author
                    session.run("""
                        MERGE (a:Author {name: $name})
                        ON CREATE SET a.paper_count = 1
                        ON MATCH SET a.paper_count = a.paper_count + 1
                    """, name=author.strip())
                    
                    # Create WROTE relationship
                    session.run("""
                        MATCH (a:Author {name: $author}), (p:Paper {title: $title})
                        MERGE (a)-[:WROTE {year: $year}]->(p)
                    """, author=author.strip(), title=paper_title, year=data.get('year'))
            
            # Add journal
            journal = data.get('journal', '').strip()
            if journal:
                session.run("""
                    MERGE (j:Journal {name: $name})
                    MATCH (p:Paper {title: $title}), (j:Journal {name: $name})
                    MERGE (p)-[:PUBLISHED_IN {year: $year}]->(j)
                """, name=journal, title=paper_title, year=data.get('year'))
            
            # Add citations
            cited_papers = data.get('cited_papers', [])
            if isinstance(cited_papers, str):
                cited_papers = [c.strip() for c in cited_papers.split(',')]
            
            for cited_paper in cited_papers:
                if cited_paper.strip():
                    # Create cited paper if it doesn't exist
                    session.run("""
                        MERGE (cp:Paper {title: $title})
                        ON CREATE SET cp.citation_count = 1
                        ON MATCH SET cp.citation_count = cp.citation_count + 1
                    """, title=cited_paper.strip())
                    
                    # Create CITES relationship
                    session.run("""
                        MATCH (p:Paper {title: $citing}), (cp:Paper {title: $cited})
                        MERGE (p)-[:CITES {year: $year, strength: 1}]->(cp)
                    """, citing=paper_title, cited=cited_paper.strip(), year=data.get('year'))
        
        # Clear relevant caches
        cache.clear_pattern("author_papers:*")
        cache.clear_pattern("influential_papers")
        
        return jsonify({'success': True, 'message': 'Paper added successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2.3 Optimized Author Query

```python
@app.route('/api/query/author/<author_name>')
@monitor_performance
@cache_result(expiry=3600)  # Cache for 1 hour
def query_papers_by_author(author_name):
    """Get all papers by an author with optimized Neo4j query"""
    try:
        with db.driver.session() as session:
            result = session.run("""
                MATCH (a:Author {name: $author_name})-[:WROTE]->(p:Paper)
                OPTIONAL MATCH (p)-[:PUBLISHED_IN]->(j:Journal)
                OPTIONAL MATCH (p)-[:CITES]->(cited:Paper)
                WITH a, p, j, count(cited) as citations
                RETURN p.title as title,
                       p.year as year,
                       j.name as journal,
                       citations,
                       a.paper_count as total_papers
                ORDER BY p.year DESC, citations DESC
            """, author_name=author_name)
            
            papers = []
            total_papers = 0
            
            for record in result:
                papers.append({
                    'title': record['title'],
                    'year': record['year'],
                    'journal': record['journal'],
                    'citations': record['citations']
                })
                total_papers = record['total_papers']
            
            return jsonify({
                'author': author_name,
                'count': len(papers),
                'total_papers': total_papers,
                'papers': papers
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2.4 Enhanced Citation Chain Query

```python
@app.route('/api/query/citations/<paper_title>')
@monitor_performance
@cache_result(expiry=7200)  # Cache for 2 hours
def query_citations(paper_title):
    """Get citation analysis with optimized Neo4j traversal"""
    try:
        with db.driver.session() as session:
            # Get papers this paper cites
            cites_result = session.run("""
                MATCH (p:Paper {title: $title})-[:CITES]->(cited:Paper)
                RETURN cited.title as title, cited.citation_count as citations
                ORDER BY citations DESC
            """, title=paper_title)
            
            cites = [record['title'] for record in cites_result]
            
            # Get papers that cite this paper
            cited_by_result = session.run("""
                MATCH (citing:Paper)-[:CITES]->(p:Paper {title: $title})
                RETURN citing.title as title, citing.citation_count as citations
                ORDER BY citations DESC
            """, title=paper_title)
            
            cited_by = [record['title'] for record in cited_by_result]
            
            # Get citation chain (papers cited by papers that cite this paper)
            chain_result = session.run("""
                MATCH (citing:Paper)-[:CITES]->(p:Paper {title: $title})
                MATCH (citing)-[:CITES]->(chain:Paper)
                WHERE chain <> p
                RETURN chain.title as title, count(citing) as strength
                ORDER BY strength DESC
                LIMIT 20
            """, title=paper_title)
            
            citation_chain = [record['title'] for record in chain_result]
            
            return jsonify({
                'paper': paper_title,
                'citations_count': len(cites),
                'cited_by_count': len(cited_by),
                'cites': cites,
                'cited_by': cited_by,
                'citation_chain': citation_chain
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2.5 Influential Papers Query

```python
@app.route('/api/influential')
@monitor_performance
@cache_result(expiry=21600)  # Cache for 6 hours
def get_influential_papers():
    """Get most influential papers based on citation count"""
    try:
        with db.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper)
                OPTIONAL MATCH (p)-[:PUBLISHED_IN]->(j:Journal)
                OPTIONAL MATCH (p)-[:CITES]->(cited:Paper)
                WITH p, j, count(cited) as citations
                WHERE citations > 0
                RETURN p.title as title,
                       p.year as year,
                       j.name as journal,
                       citations,
                       p.citation_count as total_citations
                ORDER BY total_citations DESC, citations DESC
                LIMIT 50
            """)
            
            papers = []
            for record in result:
                papers.append({
                    'title': record['title'],
                    'year': record['year'],
                    'journal': record['journal'],
                    'citation_count': record['total_citations'],
                    'outgoing_citations': record['citations']
                })
            
            return jsonify(papers)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 3. Data Migration Script

```python
# scripts/migrate_to_neo4j.py
import networkx as nx
import json
from config.database import db

def migrate_networkx_to_neo4j():
    """Migrate existing NetworkX graph to Neo4j"""
    
    # Load existing NetworkX graph
    knowledge_graph = nx.MultiDiGraph()
    
    # Load data from existing files or recreate graph
    # This would load your existing data
    
    print("Starting migration to Neo4j...")
    
    with db.driver.session() as session:
        # Create constraints and indexes
        db.create_constraints_and_indexes()
        
        # Migrate nodes
        for node, data in knowledge_graph.nodes(data=True):
            if data.get('type') == 'paper':
                session.run("""
                    MERGE (p:Paper {title: $title})
                    SET p.year = $year,
                        p.journal = $journal,
                        p.authors = $authors
                """, title=node, year=data.get('year'), 
                     journal=data.get('journal'), 
                     authors=data.get('authors', []))
            
            elif data.get('type') == 'author':
                session.run("""
                    MERGE (a:Author {name: $name})
                    SET a.paper_count = $paper_count
                """, name=node, paper_count=data.get('paper_count', 0))
            
            elif data.get('type') == 'journal':
                session.run("""
                    MERGE (j:Journal {name: $name})
                """, name=node)
        
        # Migrate relationships
        for source, target, data in knowledge_graph.edges(data=True):
            if data.get('type') == 'cites':
                session.run("""
                    MATCH (p1:Paper {title: $source}), (p2:Paper {title: $target})
                    MERGE (p1)-[:CITES {year: $year}]->(p2)
                """, source=source, target=target, year=data.get('year'))
            
            elif data.get('type') == 'wrote':
                session.run("""
                    MATCH (a:Author {name: $author}), (p:Paper {title: $paper})
                    MERGE (a)-[:WROTE {year: $year}]->(p)
                """, author=source, paper=target, year=data.get('year'))
            
            elif data.get('type') == 'published_in':
                session.run("""
                    MATCH (p:Paper {title: $paper}), (j:Journal {name: $journal})
                    MERGE (p)-[:PUBLISHED_IN {year: $year}]->(j)
                """, paper=source, journal=target, year=data.get('year'))
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_networkx_to_neo4j()
```

## 4. Performance Monitoring

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
QUERY_DURATION = Histogram('query_duration_seconds', 'Query duration in seconds', ['endpoint'])
QUERY_COUNT = Counter('query_total', 'Total number of queries', ['endpoint'])
CACHE_HIT_RATIO = Gauge('cache_hit_ratio', 'Cache hit ratio percentage')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active database connections')

def monitor_query(endpoint):
    """Decorator to monitor query performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            QUERY_COUNT.labels(endpoint=endpoint).inc()
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                QUERY_DURATION.labels(endpoint=endpoint).observe(duration)
        return wrapper
    return decorator
```

## 5. Environment Configuration

```bash
# .env file
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
FLASK_ENV=production
```

## 6. Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_HOST=redis
    depends_on:
      - neo4j
      - redis
  
  neo4j:
    image: neo4j:5.14.1
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  neo4j_data:
  redis_data:
```

## 7. Testing Script

```python
# tests/performance_test.py
import requests
import time
import statistics

def test_performance():
    """Test API performance"""
    base_url = "http://localhost:5000"
    
    # Test author query
    print("Testing author query performance...")
    author_times = []
    for i in range(10):
        start = time.time()
        response = requests.get(f"{base_url}/api/query/author/John%20Doe")
        duration = time.time() - start
        author_times.append(duration)
        print(f"Query {i+1}: {duration:.3f}s")
    
    print(f"Author query average: {statistics.mean(author_times):.3f}s")
    print(f"Author query median: {statistics.median(author_times):.3f}s")
    
    # Test citation query
    print("\nTesting citation query performance...")
    citation_times = []
    for i in range(10):
        start = time.time()
        response = requests.get(f"{base_url}/api/query/citations/Sample%20Paper")
        duration = time.time() - start
        citation_times.append(duration)
        print(f"Query {i+1}: {duration:.3f}s")
    
    print(f"Citation query average: {statistics.mean(citation_times):.3f}s")
    print(f"Citation query median: {statistics.median(citation_times):.3f}s")

if __name__ == "__main__":
    test_performance()
```

This implementation guide provides working code examples for all major components of the enhancement plan. Follow the steps in order to implement the scalable academic knowledge graph system. 