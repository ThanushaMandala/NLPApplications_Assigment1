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
- **Neo4j Database** (optional, for enhanced performance)
- **Redis Cache** (optional, for improved response times)

### Database Setup (Optional)

The application supports both in-memory storage (default) and Neo4j graph database for enhanced performance and scalability.

#### Option 1: In-Memory Storage (Default)
- No additional setup required
- Data is stored in memory during application runtime
- Suitable for development and small datasets

#### Option 2: Neo4j Graph Database (Recommended for Production)

1. **Install Neo4j**
   ```bash
   # Using Docker (recommended)
   docker run \
       --name neo4j \
       -p 7474:7474 -p 7687:7687 \
       -e NEO4J_AUTH=neo4j/password123 \
       -e NEO4J_PLUGINS='["apoc"]' \
       -v neo4j_data:/data \
       neo4j:5.14.1
   
   # Or download from https://neo4j.com/download/
   ```

2. **Create Environment Configuration**
   ```bash
   # Create .env file in project root
   cat > .env << EOF
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password123
   EOF
   ```

3. **Verify Neo4j Connection**
   - Open Neo4j Browser at `http://localhost:7474`
   - Login with username: `neo4j`, password: `password123`
   - The application will automatically create constraints and indexes

### Cache Setup (Optional)

The application includes Redis caching for improved performance with automatic fallback to in-memory cache.

#### Option 1: In-Memory Cache (Default)
- No additional setup required
- Cache is stored in application memory
- Suitable for development and single-instance deployments

#### Option 2: Redis Cache (Recommended for Production)

1. **Install Redis**
   ```bash
   # Using Docker (recommended)
   docker run \
       --name redis \
       -p 6379:6379 \
       -v redis_data:/data \
       redis:7-alpine
   
   # Or install via package manager
   # macOS: brew install redis
   # Ubuntu: sudo apt-get install redis-server
   ```

2. **Update Environment Configuration**
   ```bash
   # Add Redis configuration to .env file
   cat >> .env << EOF
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   EOF
   ```

3. **Verify Redis Connection**
   ```bash
   # Test Redis connection
   redis-cli ping
   # Should return: PONG
   ```

### Docker Setup (Recommended for Production)

For easy deployment with all dependencies, use Docker Compose:

1. **Create docker-compose.yml**
   ```yaml
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
         - NEO4J_AUTH=neo4j/password123
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

2. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   RUN pip install neo4j py2neo redis python-dotenv
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["python", "app.py"]
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access Services**
   - Application: `http://localhost:5000`
   - Neo4j Browser: `http://localhost:7474`
   - Redis CLI: `docker exec -it redis redis-cli`

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   # Navigate to your project directory
   cd nlpa-project2
   ```

2. **Install Python dependencies**
   ```bash
   # Install basic dependencies
   pip install -r requirements.txt
   
   # Install optional dependencies for database and cache
   pip install neo4j py2neo redis python-dotenv
   ```

3. **Configure Environment (Optional)**
   ```bash
   # Copy example environment file
   cp .env.example .env
   # Edit .env with your database and cache settings
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
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

### Database Layer
- **Neo4j**: Graph database for persistent storage (optional)
- **In-Memory Storage**: Default storage using NetworkX graphs
- **Database Manager**: Automatic connection handling and fallback

### Cache Layer
- **Redis**: High-performance caching (optional)
- **In-Memory Cache**: Fallback cache when Redis is unavailable
- **Cache Manager**: Automatic cache invalidation and pattern clearing

### Frontend
- **HTML5/CSS3**: Modern, responsive interface
- **D3.js**: Interactive graph visualization
- **JavaScript**: Client-side interactivity
- **Responsive Design**: Mobile-friendly layout

### Data Model
- **Nodes**: Papers, Authors, Journals
- **Edges**: Citations, Authorship, Publication relationships
- **Metadata**: Year, journal information, author lists

## Environment Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```bash
# Database Configuration (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Cache Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j database connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password123` | Neo4j password |
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `FLASK_ENV` | `development` | Flask environment mode |
| `FLASK_DEBUG` | `True` | Enable Flask debug mode |

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

### Database Issues

5. **Neo4j connection fails**:
   - Verify Neo4j is running: `docker ps` or check service status
   - Check credentials in `.env` file
   - Ensure Neo4j Browser is accessible at `http://localhost:7474`
   - Reset Neo4j password if needed: `docker exec -it neo4j neo4j-admin set-initial-password newpassword`

6. **Database constraints error**:
   - Clear existing data: `MATCH (n) DETACH DELETE n` in Neo4j Browser
   - Restart the application to recreate constraints

### Cache Issues

7. **Redis connection fails**:
   - Verify Redis is running: `docker ps` or `redis-cli ping`
   - Check Redis configuration in `.env` file
   - Application will automatically fallback to in-memory cache

8. **Cache not working**:
   - Check Redis logs: `docker logs redis`
   - Verify Redis memory usage: `redis-cli info memory`
   - Clear cache: `redis-cli FLUSHDB`

### Performance Issues

9. **Slow queries**:
   - Enable Neo4j for persistent storage
   - Enable Redis for caching
   - Check database indexes: `SHOW INDEXES` in Neo4j Browser
   - Monitor cache hit ratio in application logs

10. **Memory issues**:
    - Increase Redis memory limit
    - Optimize Neo4j memory settings
    - Consider using Docker with resource limits

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
├── .env                  # Environment configuration (create this)
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker configuration
├── sample_data.csv       # Sample CSV data
├── sample_data.json      # Sample JSON data
├── config/
│   └── database.py       # Database configuration and manager
├── cache/
│   └── redis_cache.py    # Cache configuration and manager
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