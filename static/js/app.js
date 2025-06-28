// Global variables
let svg, g, simulation, nodes = [], links = [];
let width = 800, height = 550;
let showLabels = true;
let currentZoom = 1;
let selectedFile = null;

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeGraph();
    setupEventListeners();
    loadGraphData();
});

// Initialize the D3.js graph
function initializeGraph() {
    const container = d3.select('#graph-container');
    
    svg = container.append('svg')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');

    // Define arrowhead marker
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '-0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('orient', 'auto')
        .attr('markerWidth', 5)
        .attr('markerHeight', 5)
        .attr('xoverflow', 'visible')
        .append('svg:path')
        .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
        .attr('fill', '#999')
        .style('stroke', 'none');

    // Create main group for zooming and panning
    g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', function(event) {
            g.attr('transform', event.transform);
            currentZoom = event.transform.k;
        });

    svg.call(zoom);

    // Initialize force simulation
    simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(20));

    // Create tooltip
    const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);

    window.tooltip = tooltip;
}

// Setup all event listeners
function setupEventListeners() {
    // Paper form submission
    document.getElementById('paper-form').addEventListener('submit', handlePaperSubmission);

    // File upload handlers
    const fileUpload = document.getElementById('file-upload');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');

    fileUpload.addEventListener('click', () => fileInput.click());
    fileUpload.addEventListener('dragover', handleDragOver);
    fileUpload.addEventListener('drop', handleFileDrop);
    fileInput.addEventListener('change', handleFileSelect);
    uploadBtn.addEventListener('click', handleFileUpload);

    // Graph control buttons
    document.getElementById('zoom-in').addEventListener('click', () => zoomGraph(1.2));
    document.getElementById('zoom-out').addEventListener('click', () => zoomGraph(0.8));
    document.getElementById('reset-view').addEventListener('click', resetView);
    document.getElementById('toggle-labels').addEventListener('click', toggleLabels);
    document.getElementById('layout-force').addEventListener('click', () => setLayout('force'));
    document.getElementById('layout-circular').addEventListener('click', () => setLayout('circular'));
}

// Handle paper form submission
async function handlePaperSubmission(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const paperData = {
        title: formData.get('title').trim(),
        authors: formData.get('authors').trim(),
        journal: formData.get('journal').trim(),
        year: formData.get('year'),
        cited_papers: formData.get('cited_papers').trim()
    };

    if (!paperData.title) {
        showNotification('Paper title is required', 'error');
        return;
    }

    try {
        const response = await fetch('/api/papers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paperData)
        });

        const result = await response.json();

        if (response.ok) {
            showNotification('Paper added successfully!', 'success');
            event.target.reset();
            await loadGraphData();
        } else {
            showNotification(result.error || 'Error adding paper', 'error');
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    }
}

// File upload handlers
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'text/csv' || file.type === 'application/json' || 
            file.name.endsWith('.csv') || file.name.endsWith('.json')) {
            selectedFile = file;
            updateFileUploadUI(file.name);
        } else {
            showNotification('Please select a CSV or JSON file', 'error');
        }
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        updateFileUploadUI(file.name);
    }
}

function updateFileUploadUI(filename) {
    document.querySelector('#file-upload p').textContent = `Selected: ${filename}`;
    document.getElementById('upload-btn').style.display = 'block';
}

async function handleFileUpload() {
    if (!selectedFile) {
        showNotification('Please select a file first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        showLoading(true);
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            showNotification(result.message, 'success');
            selectedFile = null;
            document.querySelector('#file-upload p').textContent = 'Drop your CSV or JSON file here, or click to select';
            document.getElementById('upload-btn').style.display = 'none';
            await loadGraphData();
        } else {
            showNotification(result.error || 'Error uploading file', 'error');
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Load graph data from API
async function loadGraphData() {
    try {
        showLoading(true);
        const response = await fetch('/api/graph');
        const data = await response.json();

        if (response.ok) {
            nodes = data.nodes;
            links = data.links;
            updateGraph();
            updateStatistics();
        } else {
            showNotification(data.error || 'Error loading graph data', 'error');
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Update the graph visualization
function updateGraph() {
    // Clear existing elements
    g.selectAll('.link').remove();
    g.selectAll('.node').remove();
    g.selectAll('.label').remove();

    // Update simulation with new data
    simulation.nodes(nodes);
    simulation.force('link').links(links);

    // Create links
    const link = g.selectAll('.link')
        .data(links)
        .enter().append('line')
        .attr('class', d => `link ${d.type}`)
        .attr('stroke-width', 2);

    // Create nodes
    const node = g.selectAll('.node')
        .data(nodes)
        .enter().append('circle')
        .attr('class', d => `node ${d.type}`)
        .attr('r', d => {
            switch(d.type) {
                case 'paper': return 8;
                case 'author': return 6;
                case 'journal': return 10;
                default: return 5;
            }
        })
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('click', handleNodeClick)
        .on('mouseover', handleNodeMouseOver)
        .on('mouseout', handleNodeMouseOut);

    // Create labels
    const label = g.selectAll('.label')
        .data(nodes)
        .enter().append('text')
        .attr('class', 'label')
        .style('font-size', '10px')
        .style('font-family', 'Arial, sans-serif')
        .style('fill', '#333')
        .style('pointer-events', 'none')
        .style('text-anchor', 'middle')
        .style('display', showLabels ? 'block' : 'none')
        .text(d => {
            const maxLength = 15;
            const text = d.name || d.title || d.id;
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        });

    // Update positions on simulation tick
    simulation.on('tick', function() {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y + 3);
    });

    simulation.alpha(1).restart();
}

// Node interaction handlers
function handleNodeClick(event, d) {
    // Remove previous selections
    g.selectAll('.node').classed('selected', false);
    g.selectAll('.link').classed('highlighted', false);

    // Select current node
    d3.select(this).classed('selected', true);

    // Highlight connected links
    g.selectAll('.link')
        .classed('highlighted', link => link.source.id === d.id || link.target.id === d.id);

    // Show node details
    showNodeDetails(d);
}

function handleNodeMouseOver(event, d) {
    const tooltip = window.tooltip;
    
    let content = `<strong>${d.name || d.title || d.id}</strong><br/>`;
    content += `Type: ${d.type}<br/>`;
    
    if (d.type === 'paper') {
        if (d.year) content += `Year: ${d.year}<br/>`;
        if (d.journal) content += `Journal: ${d.journal}<br/>`;
        if (d.authors && d.authors.length > 0) {
            content += `Authors: ${Array.isArray(d.authors) ? d.authors.join(', ') : d.authors}`;
        }
    }

    tooltip.transition()
        .duration(200)
        .style('opacity', .9);
    
    tooltip.html(content)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
}

function handleNodeMouseOut() {
    window.tooltip.transition()
        .duration(500)
        .style('opacity', 0);
}

function showNodeDetails(d) {
    console.log('Node details:', d);
}

// Drag handlers
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Graph control functions
function zoomGraph(factor) {
    const newZoom = currentZoom * factor;
    if (newZoom >= 0.1 && newZoom <= 4) {
        svg.transition().duration(300).call(
            d3.zoom().transform,
            d3.zoomIdentity.scale(newZoom).translate(width/2, height/2)
        );
    }
}

function resetView() {
    svg.transition().duration(500).call(
        d3.zoom().transform,
        d3.zoomIdentity
    );
    currentZoom = 1;
}

function toggleLabels() {
    showLabels = !showLabels;
    g.selectAll('.label').style('display', showLabels ? 'block' : 'none');
    
    const button = document.getElementById('toggle-labels');
    button.textContent = showLabels ? 'Hide Labels' : 'Show Labels';
}

function setLayout(type) {
    if (type === 'force') {
        simulation
            .force('link', d3.forceLink().id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(20));
    } else if (type === 'circular') {
        simulation
            .force('link', null)
            .force('charge', null)
            .force('collision', null);

        const radius = Math.min(width, height) / 2 - 50;
        const angleStep = (2 * Math.PI) / nodes.length;

        nodes.forEach((node, i) => {
            const angle = i * angleStep;
            node.fx = width / 2 + radius * Math.cos(angle);
            node.fy = height / 2 + radius * Math.sin(angle);
        });
    }

    simulation.alpha(1).restart();

    // Update button states
    document.querySelectorAll('#layout-force, #layout-circular').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`layout-${type}`).classList.add('active');
}

// Update statistics
function updateStatistics() {
    const paperCount = nodes.filter(n => n.type === 'paper').length;
    const authorCount = nodes.filter(n => n.type === 'author').length;
    const journalCount = nodes.filter(n => n.type === 'journal').length;
    const citationCount = links.filter(l => l.type === 'cites').length;

    document.getElementById('papers-count').textContent = paperCount;
    document.getElementById('authors-count').textContent = authorCount;
    document.getElementById('journals-count').textContent = journalCount;
    document.getElementById('citations-count').textContent = citationCount;
}

// Query functions
async function queryAuthorPapers() {
    const authorName = document.getElementById('author-name').value.trim();
    if (!authorName) {
        showNotification('Please enter an author name', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/query/author/${encodeURIComponent(authorName)}`);
        const data = await response.json();

        const resultsDiv = document.getElementById('author-results');
        
        if (response.ok) {
            displayAuthorResults(data, resultsDiv);
        } else {
            resultsDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        }
        
        resultsDiv.style.display = 'block';
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    }
}

async function queryCitations() {
    const paperTitle = document.getElementById('paper-title-query').value.trim();
    if (!paperTitle) {
        showNotification('Please enter a paper title', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/query/citations/${encodeURIComponent(paperTitle)}`);
        const data = await response.json();

        const resultsDiv = document.getElementById('citation-results');
        
        if (response.ok) {
            displayCitationResults(data, resultsDiv);
        } else {
            resultsDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        }
        
        resultsDiv.style.display = 'block';
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    }
}

async function queryInfluentialPapers() {
    try {
        const response = await fetch('/api/influential');
        const data = await response.json();

        const resultsDiv = document.getElementById('influential-results');
        
        if (response.ok) {
            displayInfluentialResults(data, resultsDiv);
        } else {
            resultsDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        }
        
        resultsDiv.style.display = 'block';
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    }
}

// Result display functions
function displayAuthorResults(data, container) {
    let html = `<h3>Papers by ${data.author} (${data.count} found)</h3>`;
    
    if (data.papers.length === 0) {
        html += '<p>No papers found for this author.</p>';
    } else {
        data.papers.forEach(paper => {
            html += `
                <div class="result-item">
                    <h4>${paper.title}</h4>
                    ${paper.year ? `<p><strong>Year:</strong> ${paper.year}</p>` : ''}
                    ${paper.journal ? `<p><strong>Journal:</strong> ${paper.journal}</p>` : ''}
                    ${paper.authors.length > 0 ? `<p><strong>Authors:</strong> ${Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}</p>` : ''}
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
}

function displayCitationResults(data, container) {
    let html = `<h3>Citation Analysis for "${data.paper}"</h3>`;
    
    html += `
        <div class="result-item">
            <h4>Citations Statistics</h4>
            <p><strong>Papers this paper cites:</strong> ${data.citations_count}</p>
            <p><strong>Papers that cite this paper:</strong> ${data.cited_by_count}</p>
        </div>
    `;

    if (data.cites.length > 0) {
        html += '<div class="result-item"><h4>This paper cites:</h4>';
        data.cites.forEach(citedPaper => {
            html += `<p>• ${citedPaper}</p>`;
        });
        html += '</div>';
    }

    if (data.cited_by.length > 0) {
        html += '<div class="result-item"><h4>This paper is cited by:</h4>';
        data.cited_by.forEach(citingPaper => {
            html += `<p>• ${citingPaper}</p>`;
        });
        html += '</div>';
    }

    if (data.cites.length === 0 && data.cited_by.length === 0) {
        html += '<p>No citation relationships found for this paper.</p>';
    }
    
    container.innerHTML = html;
}

function displayInfluentialResults(data, container) {
    let html = '<h3>Most Influential Papers (by citation count)</h3>';
    
    if (data.length === 0) {
        html += '<p>No papers found.</p>';
    } else {
        data.forEach((paper, index) => {
            html += `
                <div class="result-item">
                    <h4>#${index + 1} ${paper.title}</h4>
                    <p><strong>Citation Count:</strong> ${paper.citation_count}</p>
                    ${paper.year ? `<p><strong>Year:</strong> ${paper.year}</p>` : ''}
                    ${paper.journal ? `<p><strong>Journal:</strong> ${paper.journal}</p>` : ''}
                    ${paper.authors.length > 0 ? `<p><strong>Authors:</strong> ${Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}</p>` : ''}
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
}

// Tab functions
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

function showQueryTab(tabName) {
    // Hide all query tab contents
    document.querySelectorAll('#author-query, #citation-query, #influential-query').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all query tabs
    document.querySelectorAll('.query-section .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

// Utility functions
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.add('show');
    } else {
        loading.classList.remove('show');
    }
} 