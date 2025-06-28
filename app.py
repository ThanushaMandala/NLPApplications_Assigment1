from flask import Flask, render_template, request, jsonify, redirect, url_for
import networkx as nx
import json
import csv
import io
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the knowledge graph
knowledge_graph = nx.MultiDiGraph()

# Store additional metadata
paper_metadata = {}
author_metadata = {}
journal_metadata = {}

@app.route('/')
def index():
    """Main page with the knowledge graph interface."""
    return render_template('index.html')

@app.route('/api/papers', methods=['GET'])
def get_papers():
    """Get all papers in the knowledge graph."""
    papers = []
    for node in knowledge_graph.nodes():
        if knowledge_graph.nodes[node].get('type') == 'paper':
            papers.append({
                'id': node,
                'title': knowledge_graph.nodes[node].get('title', node),
                'year': knowledge_graph.nodes[node].get('year', ''),
                'authors': knowledge_graph.nodes[node].get('authors', []),
                'journal': knowledge_graph.nodes[node].get('journal', '')
            })
    return jsonify(papers)

@app.route('/api/papers', methods=['POST'])
def add_paper():
    """Add a new paper to the knowledge graph."""
    try:
        data = request.get_json()
        
        paper_id = data.get('title', '').strip()
        if not paper_id:
            return jsonify({'error': 'Paper title is required'}), 400
        
        # Add paper node
        knowledge_graph.add_node(paper_id, 
                                type='paper',
                                title=paper_id,
                                year=data.get('year', ''),
                                authors=data.get('authors', []),
                                journal=data.get('journal', ''))
        
        # Add author nodes and relationships
        authors = data.get('authors', [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(',')]
        
        for author in authors:
            if author.strip():
                author = author.strip()
                knowledge_graph.add_node(author, type='author', name=author)
                knowledge_graph.add_edge(author, paper_id, type='wrote')
        
        # Add journal node and relationship
        journal = data.get('journal', '').strip()
        if journal:
            knowledge_graph.add_node(journal, type='journal', name=journal)
            knowledge_graph.add_edge(paper_id, journal, type='published_in')
        
        # Add citation relationships
        cited_papers = data.get('cited_papers', [])
        if isinstance(cited_papers, str):
            cited_papers = [c.strip() for c in cited_papers.split(',')]
        
        for cited_paper in cited_papers:
            if cited_paper.strip():
                cited_paper = cited_paper.strip()
                # Add cited paper as node if it doesn't exist
                if not knowledge_graph.has_node(cited_paper):
                    knowledge_graph.add_node(cited_paper, type='paper', title=cited_paper)
                knowledge_graph.add_edge(paper_id, cited_paper, type='cites')
        
        return jsonify({'success': True, 'message': 'Paper added successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process CSV/JSON files."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension == 'csv':
            return process_csv_file(file)
        elif file_extension == 'json':
            return process_json_file(file)
        else:
            return jsonify({'error': 'Unsupported file format. Please upload CSV or JSON files.'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_csv_file(file):
    """Process uploaded CSV file."""
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        papers_added = 0
        for row in csv_input:
            # Expected CSV columns: title, authors, journal, year, cited_papers
            paper_data = {
                'title': row.get('title', '').strip(),
                'authors': row.get('authors', '').strip(),
                'journal': row.get('journal', '').strip(),
                'year': row.get('year', '').strip(),
                'cited_papers': row.get('cited_papers', '').strip()
            }
            
            if paper_data['title']:
                # Process the paper data similar to add_paper endpoint
                paper_id = paper_data['title']
                
                knowledge_graph.add_node(paper_id,
                                        type='paper',
                                        title=paper_id,
                                        year=paper_data['year'],
                                        authors=paper_data['authors'].split(',') if paper_data['authors'] else [],
                                        journal=paper_data['journal'])
                
                # Add authors
                if paper_data['authors']:
                    authors = [a.strip() for a in paper_data['authors'].split(',')]
                    for author in authors:
                        if author:
                            knowledge_graph.add_node(author, type='author', name=author)
                            knowledge_graph.add_edge(author, paper_id, type='wrote')
                
                # Add journal
                if paper_data['journal']:
                    journal = paper_data['journal']
                    knowledge_graph.add_node(journal, type='journal', name=journal)
                    knowledge_graph.add_edge(paper_id, journal, type='published_in')
                
                # Add citations
                if paper_data['cited_papers']:
                    cited_papers = [c.strip() for c in paper_data['cited_papers'].split(',')]
                    for cited_paper in cited_papers:
                        if cited_paper:
                            if not knowledge_graph.has_node(cited_paper):
                                knowledge_graph.add_node(cited_paper, type='paper', title=cited_paper)
                            knowledge_graph.add_edge(paper_id, cited_paper, type='cites')
                
                papers_added += 1
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed CSV file. Added {papers_added} papers.'
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing CSV file: {str(e)}'}), 500

def process_json_file(file):
    """Process uploaded JSON file."""
    try:
        data = json.load(file)
        
        papers_added = 0
        if isinstance(data, list):
            for paper_data in data:
                if paper_data.get('title'):
                    # Process each paper similar to add_paper endpoint
                    paper_id = paper_data['title']
                    
                    knowledge_graph.add_node(paper_id,
                                            type='paper',
                                            title=paper_id,
                                            year=paper_data.get('year', ''),
                                            authors=paper_data.get('authors', []),
                                            journal=paper_data.get('journal', ''))
                    
                    # Add authors
                    authors = paper_data.get('authors', [])
                    if isinstance(authors, str):
                        authors = [a.strip() for a in authors.split(',')]
                    
                    for author in authors:
                        if author.strip():
                            author = author.strip()
                            knowledge_graph.add_node(author, type='author', name=author)
                            knowledge_graph.add_edge(author, paper_id, type='wrote')
                    
                    # Add journal
                    journal = paper_data.get('journal', '').strip()
                    if journal:
                        knowledge_graph.add_node(journal, type='journal', name=journal)
                        knowledge_graph.add_edge(paper_id, journal, type='published_in')
                    
                    # Add citations
                    cited_papers = paper_data.get('cited_papers', [])
                    if isinstance(cited_papers, str):
                        cited_papers = [c.strip() for c in cited_papers.split(',')]
                    
                    for cited_paper in cited_papers:
                        if cited_paper.strip():
                            cited_paper = cited_paper.strip()
                            if not knowledge_graph.has_node(cited_paper):
                                knowledge_graph.add_node(cited_paper, type='paper', title=cited_paper)
                            knowledge_graph.add_edge(paper_id, cited_paper, type='cites')
                    
                    papers_added += 1
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed JSON file. Added {papers_added} papers.'
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing JSON file: {str(e)}'}), 500

@app.route('/api/query/author/<author_name>')
def query_papers_by_author(author_name):
    """Query all papers written by a specific author."""
    try:
        papers = []
        if knowledge_graph.has_node(author_name):
            # Find all papers this author wrote
            for neighbor in knowledge_graph.neighbors(author_name):
                edge_data = knowledge_graph.get_edge_data(author_name, neighbor)
                if any(edge.get('type') == 'wrote' for edge in edge_data.values()):
                    paper_node = knowledge_graph.nodes[neighbor]
                    if paper_node.get('type') == 'paper':
                        papers.append({
                            'title': neighbor,
                            'year': paper_node.get('year', ''),
                            'journal': paper_node.get('journal', ''),
                            'authors': paper_node.get('authors', [])
                        })
        
        return jsonify({
            'author': author_name,
            'papers': papers,
            'count': len(papers)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/citations/<paper_title>')
def query_citations(paper_title):
    """Find papers that cite a particular paper."""
    try:
        citing_papers = []
        cited_by_papers = []
        
        if knowledge_graph.has_node(paper_title):
            # Find papers that this paper cites
            for neighbor in knowledge_graph.neighbors(paper_title):
                edge_data = knowledge_graph.get_edge_data(paper_title, neighbor)
                if any(edge.get('type') == 'cites' for edge in edge_data.values()):
                    citing_papers.append(neighbor)
            
            # Find papers that cite this paper
            for node in knowledge_graph.nodes():
                if node != paper_title:
                    if knowledge_graph.has_edge(node, paper_title):
                        edge_data = knowledge_graph.get_edge_data(node, paper_title)
                        if any(edge.get('type') == 'cites' for edge in edge_data.values()):
                            cited_by_papers.append(node)
        
        return jsonify({
            'paper': paper_title,
            'cites': citing_papers,
            'cited_by': cited_by_papers,
            'citations_count': len(citing_papers),
            'cited_by_count': len(cited_by_papers)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graph')
def get_graph_data():
    """Get the complete graph data for visualization."""
    try:
        nodes = []
        links = []
        
        # Collect nodes
        for node_id in knowledge_graph.nodes():
            node_data = knowledge_graph.nodes[node_id]
            node_type = node_data.get('type', 'unknown')
            
            nodes.append({
                'id': node_id,
                'type': node_type,
                'title': node_data.get('title', node_id),
                'name': node_data.get('name', node_id),
                'year': node_data.get('year', ''),
                'authors': node_data.get('authors', []),
                'journal': node_data.get('journal', '')
            })
        
        # Collect edges
        for source, target, data in knowledge_graph.edges(data=True):
            links.append({
                'source': source,
                'target': target,
                'type': data.get('type', 'unknown')
            })
        
        return jsonify({
            'nodes': nodes,
            'links': links
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/influential')
def get_influential_papers():
    """Get most influential papers based on citation count."""
    try:
        citation_counts = {}
        
        # Count citations for each paper
        for node in knowledge_graph.nodes():
            if knowledge_graph.nodes[node].get('type') == 'paper':
                citation_count = 0
                for other_node in knowledge_graph.nodes():
                    if other_node != node and knowledge_graph.has_edge(other_node, node):
                        edge_data = knowledge_graph.get_edge_data(other_node, node)
                        if any(edge.get('type') == 'cites' for edge in edge_data.values()):
                            citation_count += 1
                citation_counts[node] = citation_count
        
        # Sort by citation count
        influential_papers = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        result = []
        for paper, count in influential_papers:
            paper_data = knowledge_graph.nodes[paper]
            result.append({
                'title': paper,
                'citation_count': count,
                'year': paper_data.get('year', ''),
                'authors': paper_data.get('authors', []),
                'journal': paper_data.get('journal', '')
            })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 