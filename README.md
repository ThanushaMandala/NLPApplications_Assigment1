# Academic Knowledge Graph Web Application

A comprehensive web-based application for modeling and visualizing relationships between academic papers, authors, journals, and citations. This application helps track knowledge flow and research influence through interactive graph visualization.

## Features

### 🌐 Web Interface
- **Clean, responsive design** with modern UI/UX
- **Real-time graph visualization** using D3.js
- **Interactive controls** for graph manipulation
- **Drag-and-drop file upload** support

### 📊 Data Management
- **Manual paper entry** with comprehensive metadata
- **Bulk data upload** via CSV/JSON files
- **Real-time graph updates** after each addition
- **Support for complex citation relationships**

### 🔍 Query Capabilities
- **Author-based queries**: Find all papers by specific authors
- **Citation analysis**: Explore citation relationships and chains
- **Influential paper detection**: Identify highly-cited research
- **Interactive graph exploration** with highlighting

### 📈 Visualization Features
- **Multi-node types**: Papers (blue), Authors (green), Journals (orange)
- **Relationship visualization**: Citations, authorship, publication
- **Interactive controls**: Zoom, pan, drag nodes
- **Layout options**: Force-directed and circular layouts
- **Hover tooltips** with detailed information

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   # Navigate to your project directory
   cd nlpa-project2
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`

## Usage Guide

### Adding Papers Manually

1. **Navigate to the "Add Paper" tab** in the sidebar
2. **Fill in the paper details**:
   - Paper Title (required)
   - Authors (comma-separated)
   - Journal Name
   - Year of Publication
   - Cited Papers (comma-separated titles)
3. **Click "Add Paper"** to submit

### Uploading Data Files

#### CSV Format
Use the following CSV structure:
```csv
title,authors,journal,year,cited_papers
"Paper Title","Author 1, Author 2","Journal Name",2023,"Cited Paper 1, Cited Paper 2"
```

#### JSON Format
Use the following JSON structure:
```json
[
    {
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "journal": "Journal Name",
        "year": "2023",
        "cited_papers": ["Cited Paper 1", "Cited Paper 2"]
    }
]
```

### Querying the Knowledge Graph

#### Author Papers Query
1. **Go to the "Author Papers" query tab**
2. **Enter an author name**
3. **Click "Find Papers"** to see all papers by that author

#### Citation Analysis
1. **Go to the "Citations" query tab**
2. **Enter a paper title**
3. **Click "Find Citations"** to see citation relationships

#### Influential Papers
1. **Go to the "Influential Papers" query tab**
2. **Click "Get Most Influential Papers"** to see highly-cited research

### Graph Visualization Controls

- **Zoom In/Out**: Use zoom buttons or mouse wheel
- **Reset View**: Return to original view
- **Toggle Labels**: Show/hide node labels
- **Layout Options**: Switch between force-directed and circular layouts
- **Node Interaction**: Click nodes to highlight connections
- **Drag Nodes**: Drag to reposition nodes manually

## API Endpoints

The application provides RESTful API endpoints:

- `GET /api/papers` - Get all papers
- `POST /api/papers` - Add a new paper
- `POST /api/upload` - Upload CSV/JSON file
- `GET /api/query/author/<author_name>` - Query papers by author
- `GET /api/query/citations/<paper_title>` - Get citation information
- `GET /api/graph` - Get complete graph data
- `GET /api/influential` - Get most influential papers

## Sample Data

The repository includes sample data files:

- `sample_data.csv` - CSV format with NLP/ML papers
- `sample_data.json` - JSON format with Graph Neural Network papers

You can upload these files to quickly populate the knowledge graph and explore the features.

## Technical Architecture

### Backend (Flask)
- **Flask**: Web framework for API and routing
- **NetworkX**: Graph data structure and algorithms
- **Pandas**: Data processing for file uploads
- **Python**: Core application logic

### Frontend
- **HTML5/CSS3**: Modern, responsive interface
- **D3.js**: Interactive graph visualization
- **JavaScript**: Client-side interactivity
- **Responsive Design**: Mobile-friendly layout

### Data Model
- **Nodes**: Papers, Authors, Journals
- **Edges**: Citations, Authorship, Publication relationships
- **Metadata**: Year, journal information, author lists

## Use Cases

### Research Influence Mapping
- **Track citation patterns** across academic papers
- **Identify influential research** in specific domains
- **Analyze collaboration networks** between authors
- **Explore knowledge flow** through citation chains

### Academic Research Tools
- **Literature review assistance** by visualizing paper relationships
- **Research trend analysis** through temporal citation patterns
- **Author impact assessment** via publication and citation metrics
- **Journal influence mapping** across different research areas

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py`
2. **File upload fails**: Check file format (CSV/JSON only)
3. **Graph not loading**: Check browser console for JavaScript errors
4. **Missing dependencies**: Run `pip install -r requirements.txt`

### Browser Compatibility
- **Chrome**: Fully supported
- **Firefox**: Fully supported
- **Safari**: Fully supported
- **Edge**: Fully supported

## Development

### File Structure
```
nlpa-project2/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── sample_data.csv       # Sample CSV data
├── sample_data.json      # Sample JSON data
├── templates/
│   └── index.html        # Main HTML template
└── static/
    └── js/
        └── app.js        # JavaScript application
```

### Extending the Application

You can extend the application by:
- Adding new node types (e.g., conferences, keywords)
- Implementing advanced graph algorithms
- Adding export functionality
- Creating user authentication
- Adding database persistence

## License

This application is created for educational purposes as part of an NLP Applications project.

## Support

For issues or questions about the application, please refer to the code comments and this documentation. 