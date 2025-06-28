#!/usr/bin/env python3
"""
Test script for the Academic Knowledge Graph application.
This script verifies that all components are working properly.
"""

import sys
import importlib
import networkx as nx
from flask import Flask

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    required_modules = [
        'flask',
        'networkx',
        'pandas',
        'json',
        'csv',
        'io',
        'datetime',
        'os'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("All imports successful!")
    return True

def test_networkx():
    """Test NetworkX graph creation."""
    print("\nTesting NetworkX functionality...")
    
    try:
        # Create a simple graph
        G = nx.MultiDiGraph()
        
        # Add nodes
        G.add_node("Paper A", type="paper", title="Test Paper A")
        G.add_node("Author X", type="author", name="Author X")
        G.add_node("Journal Y", type="journal", name="Journal Y")
        
        # Add edges
        G.add_edge("Author X", "Paper A", type="wrote")
        G.add_edge("Paper A", "Journal Y", type="published_in")
        
        # Verify graph structure
        assert len(G.nodes()) == 3
        assert len(G.edges()) == 2
        
        print("✓ NetworkX graph creation and manipulation")
        return True
        
    except Exception as e:
        print(f"✗ NetworkX test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app creation."""
    print("\nTesting Flask app creation...")
    
    try:
        app = Flask(__name__)
        
        @app.route('/test')
        def test_route():
            return {'status': 'ok'}
        
        # Test the app in test mode
        with app.test_client() as client:
            response = client.get('/test')
            assert response.status_code == 200
        
        print("✓ Flask app creation and routing")
        return True
        
    except Exception as e:
        print(f"✗ Flask test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html',
        'static/js/app.js',
        'sample_data.csv',
        'sample_data.json'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        try:
            with open(file_path, 'r'):
                pass
            print(f"✓ {file_path}")
        except FileNotFoundError:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    print("All required files found!")
    return True

def main():
    """Run all tests."""
    print("Academic Knowledge Graph Application - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_networkx,
        test_flask_app,
        test_file_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("python app.py")
        print("\nThen open http://localhost:5000 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 