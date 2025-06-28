from neo4j import GraphDatabase
from py2neo import Graph, Node, Relationship
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jManager:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password123')
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.graph = Graph(self.uri, auth=(self.user, self.password))
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()['test'] == 1
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def create_constraints_and_indexes(self):
        """Create database constraints and indexes for optimal performance"""
        try:
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
                
                print("✅ Database constraints and indexes created successfully")
        except Exception as e:
            print(f"❌ Error creating constraints and indexes: {e}")
    
    def close(self):
        self.driver.close()

# Global database instance
db = Neo4jManager() 