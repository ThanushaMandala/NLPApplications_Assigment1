# Sample Data Guide for Academic Knowledge Graph

This guide describes all the sample data files available for testing the Academic Knowledge Graph application. Each dataset is designed to test different aspects and scenarios of the system.

## 📊 Available Sample Datasets

### 1. **Original Sample Data (Basic Testing)**

#### `sample_data.csv` (2.5KB, 10 papers)
- **Focus**: Transformer and NLP research papers
- **Content**: High-impact papers like "Attention Is All You Need", BERT, GPT-3
- **Use Case**: Basic functionality testing, citation relationships
- **Features**: Real academic papers with accurate citation relationships

#### `sample_data.json` (2.0KB, 6 papers)
- **Focus**: Graph Neural Networks research
- **Content**: GCN, GAT, GraphSAGE papers
- **Use Case**: JSON upload testing, GNN domain exploration
- **Features**: Modern graph learning papers with realistic citations

### 2. **Comprehensive Research Data (Advanced Testing)**

#### `sample_data_large.csv` (10KB, 40+ papers)
- **Focus**: Comprehensive machine learning and AI research
- **Content**: Deep learning classics, computer vision, NLP, reinforcement learning
- **Use Case**: Large dataset testing, multi-domain visualization
- **Features**: Spans multiple AI subfields with complex citation networks

#### `sample_data_nlp.json` (5KB, 22 papers)
- **Focus**: Natural Language Processing evolution
- **Content**: From Word2Vec to modern BERT variants
- **Use Case**: Domain-specific analysis, NLP research trends
- **Features**: Shows evolution of NLP techniques over time

#### `sample_data_computer_vision.csv` (8KB, 35 papers)
- **Focus**: Computer vision research history
- **Content**: From edge detection to modern object detection
- **Use Case**: Computer vision domain analysis
- **Features**: Traces CV evolution from classical to deep learning methods

### 3. **Edge Cases and Stress Testing**

#### `sample_data_edge_cases.json` (4KB, 20 papers)
- **Focus**: Testing system robustness
- **Content**: Various edge cases and unusual scenarios
- **Use Case**: Bug testing, system limits, data validation
- **Features**:
  - Papers with no authors
  - Very long titles
  - Self-referential citations
  - Empty fields
  - Special characters
  - Future publication dates
  - Duplicate citations
  - Non-existent cited papers

### 4. **Programmatic Data Generation**

#### `generate_test_data.py` (7KB, Python script)
- **Purpose**: Generate custom test datasets programmatically
- **Capabilities**:
  - Citation networks with realistic patterns
  - Research group collaboration data
  - Highly cited paper scenarios
  - Performance testing datasets (100+ papers)
- **Usage**: `python generate_test_data.py`
- **Output**: Creates multiple CSV/JSON files for different scenarios

## 🎯 Testing Scenarios by Dataset

### Basic Functionality Testing
```
Use: sample_data.csv or sample_data.json
Purpose: Verify core features work correctly
```

### Multi-Domain Knowledge Graphs
```
Use: sample_data_large.csv
Purpose: Test visualization of diverse research areas
```

### Domain-Specific Analysis
```
Use: sample_data_nlp.json or sample_data_computer_vision.csv
Purpose: Test specialized research domain insights
```

### System Robustness
```
Use: sample_data_edge_cases.json
Purpose: Test error handling and edge cases
```

### Performance Testing
```
Use: python generate_test_data.py (generates large datasets)
Purpose: Test system performance with large graphs
```

### Research Group Analysis
```
Use: generated_research_group.json (after running generator)
Purpose: Test collaboration network visualization
```

### Citation Impact Analysis
```
Use: generated_highly_cited.json (after running generator)
Purpose: Test influential paper detection
```

## 📈 Data Statistics Summary

| Dataset | Papers | Authors | Journals | Citations | Special Features |
|---------|--------|---------|----------|-----------|------------------|
| sample_data.csv | 10 | 25+ | 8 | 20+ | Real NLP papers |
| sample_data.json | 6 | 15+ | 5 | 10+ | GNN focus |
| sample_data_large.csv | 40+ | 100+ | 15+ | 80+ | Multi-domain |
| sample_data_nlp.json | 22 | 50+ | 12 | 40+ | NLP evolution |
| sample_data_computer_vision.csv | 35 | 80+ | 12 | 60+ | CV history |
| sample_data_edge_cases.json | 20 | 30+ | 15 | 25+ | Edge cases |

## 🚀 Quick Start Testing

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Start the Application**
```bash
python app.py
```

### 3. **Test Basic Upload**
- Go to http://localhost:5000
- Upload `sample_data.csv` to see transformer research network
- Try queries: "Ashish Vaswani", "BERT", "Attention Is All You Need"

### 4. **Test JSON Upload**
- Upload `sample_data.json` to add GNN papers
- Try query: "Thomas N. Kipf"

### 5. **Test Large Dataset**
- Upload `sample_data_large.csv` for comprehensive AI research graph
- Use "Influential Papers" to see most cited works

### 6. **Test Edge Cases**
- Upload `sample_data_edge_cases.json`
- Look for handling of unusual data patterns

### 7. **Generate Custom Data**
```bash
python generate_test_data.py
```
- Upload generated files for custom testing scenarios

## 🔍 Query Testing Examples

### Author Queries to Try
- "Geoffrey E. Hinton" (appears in multiple datasets)
- "Yoshua Bengio" (deep learning pioneer)
- "Ian Goodfellow" (GAN creator)
- "Ashish Vaswani" (transformer author)

### Citation Analysis Examples
- "Attention Is All You Need" (highly cited)
- "ImageNet Classification with Deep Convolutional Neural Networks" (AlexNet)
- "Generative Adversarial Networks"
- "BERT: Pre-training of Deep Bidirectional Transformers"

### Expected Results
- **Most Influential Papers**: Should show highly cited foundational works
- **Author Networks**: Should reveal collaboration patterns
- **Citation Chains**: Should trace knowledge flow through time

## 🛠️ Creating Custom Test Data

### Manual Entry Testing
1. Use the "Add Paper" form to test manual entry
2. Try various input combinations
3. Test citation relationships with existing papers

### Custom CSV Format
```csv
title,authors,journal,year,cited_papers
"Your Paper Title","Author 1, Author 2","Journal Name",2023,"Cited Paper 1, Cited Paper 2"
```

### Custom JSON Format
```json
[
  {
    "title": "Your Paper Title",
    "authors": ["Author 1", "Author 2"],
    "journal": "Journal Name", 
    "year": "2023",
    "cited_papers": ["Cited Paper 1", "Cited Paper 2"]
  }
]
```

## 📊 Visualization Testing

### Expected Graph Features
- **Blue nodes**: Papers
- **Green nodes**: Authors  
- **Orange nodes**: Journals
- **Colored edges**: Different relationship types
- **Interactive tooltips**: Paper details on hover
- **Drag functionality**: Repositionable nodes
- **Zoom/pan controls**: Navigation tools

### Layout Testing
- **Force-directed**: Default physics-based layout
- **Circular**: Nodes arranged in circle
- **Manual positioning**: Drag nodes to custom positions

This comprehensive sample data collection ensures thorough testing of all Knowledge Graph application features across various academic research scenarios. 