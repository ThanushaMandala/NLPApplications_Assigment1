#!/usr/bin/env python3
"""
Test data generator for the Academic Knowledge Graph application.
This script generates various types of sample data for testing different scenarios.
"""

import json
import csv
import random
from datetime import datetime, timedelta

# Sample data pools
COMPUTER_SCIENCE_TOPICS = [
    "Machine Learning", "Deep Learning", "Natural Language Processing", 
    "Computer Vision", "Robotics", "Distributed Systems", "Databases",
    "Algorithms", "Data Structures", "Software Engineering", "Cybersecurity",
    "Human-Computer Interaction", "Artificial Intelligence", "Blockchain",
    "Cloud Computing", "Big Data", "Internet of Things", "Quantum Computing"
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "David", "Sarah", "Michael", "Emma", "John", "Maria", "Robert", "Lisa",
    "James", "Jennifer", "William", "Jessica", "Andrew", "Ashley", "Daniel", "Amanda"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
]

JOURNALS = [
    "Journal of Computer Science Research",
    "IEEE Transactions on Pattern Analysis and Machine Intelligence",
    "ACM Computing Surveys",
    "Nature Machine Intelligence",
    "Science Robotics",
    "Artificial Intelligence Review",
    "International Conference on Machine Learning",
    "Conference on Neural Information Processing Systems",
    "International Conference on Learning Representations",
    "Computer Vision and Pattern Recognition",
    "Association for Computational Linguistics",
    "arXiv preprint",
    "IEEE Computer",
    "Communications of the ACM",
    "Journal of Machine Learning Research"
]

def generate_author_name():
    """Generate a random author name."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def generate_paper_title(topic=None):
    """Generate a random paper title."""
    if topic is None:
        topic = random.choice(COMPUTER_SCIENCE_TOPICS)
    
    prefixes = [
        "A Novel Approach to", "Deep Learning for", "Advances in", "A Survey of",
        "Efficient Methods for", "Scalable", "Robust", "Adaptive", "Intelligent",
        "Automated", "Real-time", "Distributed", "Privacy-Preserving"
    ]
    
    suffixes = [
        "Systems", "Applications", "Methods", "Algorithms", "Frameworks",
        "Models", "Architectures", "Optimization", "Analysis", "Classification",
        "Prediction", "Recognition", "Detection", "Processing"
    ]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    return f"{prefix} {topic} {suffix}"

def generate_year():
    """Generate a random publication year between 1990 and 2024."""
    return random.randint(1990, 2024)

def generate_citation_network(num_papers=50):
    """Generate a citation network with realistic patterns."""
    papers = []
    
    # Generate papers with temporal ordering
    for i in range(num_papers):
        authors = [generate_author_name() for _ in range(random.randint(1, 4))]
        title = generate_paper_title()
        journal = random.choice(JOURNALS)
        year = generate_year()
        
        # Citations should only reference earlier papers
        possible_citations = papers[:i]  # Only earlier papers
        
        # Probability of citation decreases with age difference
        cited_papers = []
        if possible_citations:
            num_citations = min(random.randint(0, 6), len(possible_citations))
            
            # Bias towards more recent papers
            weights = [1.0 / (i - j + 1) for j in range(len(possible_citations))]
            cited_indices = random.choices(
                range(len(possible_citations)), 
                weights=weights, 
                k=num_citations
            )
            
            cited_papers = [possible_citations[idx]['title'] for idx in cited_indices]
        
        papers.append({
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': str(year),
            'cited_papers': cited_papers
        })
    
    return papers

def generate_research_group_data():
    """Generate data simulating a research group's publications."""
    principal_investigator = "Dr. Research Leader"
    group_members = [generate_author_name() for _ in range(8)]
    
    papers = []
    research_topics = random.sample(COMPUTER_SCIENCE_TOPICS, 3)
    
    for i in range(20):
        # Vary collaboration patterns
        if random.random() < 0.3:  # Solo work
            authors = [random.choice(group_members)]
        elif random.random() < 0.6:  # Small collaboration
            authors = random.sample(group_members, random.randint(2, 3))
        else:  # Large collaboration with PI
            authors = [principal_investigator] + random.sample(group_members, random.randint(2, 5))
        
        topic = random.choice(research_topics)
        title = generate_paper_title(topic)
        journal = random.choice(JOURNALS)
        year = random.randint(2018, 2024)
        
        # Internal citations within the group
        cited_papers = []
        if i > 0:
            num_internal_citations = random.randint(0, min(3, i))
            cited_papers = random.sample([p['title'] for p in papers], num_internal_citations)
        
        papers.append({
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': str(year),
            'cited_papers': cited_papers
        })
    
    return papers

def generate_highly_cited_paper_scenario():
    """Generate data with a highly cited foundational paper."""
    papers = []
    
    # Foundational paper
    foundational_paper = {
        'title': "Foundational Work in Advanced Computing",
        'authors': ["Pioneer Researcher", "Co-Founder"],
        'journal': "Nature",
        'year': "2010",
        'cited_papers': []
    }
    papers.append(foundational_paper)
    
    # Papers that cite the foundational work
    for i in range(25):
        authors = [generate_author_name() for _ in range(random.randint(1, 3))]
        title = generate_paper_title()
        journal = random.choice(JOURNALS)
        year = random.randint(2011, 2024)
        
        # High probability of citing the foundational paper
        cited_papers = []
        if random.random() < 0.8:  # 80% chance
            cited_papers.append(foundational_paper['title'])
        
        # Also cite some other papers
        if i > 0:
            other_citations = random.sample([p['title'] for p in papers[1:i]], 
                                         random.randint(0, min(2, i)))
            cited_papers.extend(other_citations)
        
        papers.append({
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': str(year),
            'cited_papers': cited_papers
        })
    
    return papers

def save_as_csv(papers, filename):
    """Save papers data as CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'authors', 'journal', 'year', 'cited_papers']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for paper in papers:
            # Convert authors list to comma-separated string
            authors_str = ', '.join(paper['authors']) if paper['authors'] else ''
            # Convert cited_papers list to comma-separated string
            cited_str = ', '.join(paper['cited_papers']) if paper['cited_papers'] else ''
            
            writer.writerow({
                'title': paper['title'],
                'authors': authors_str,
                'journal': paper['journal'],
                'year': paper['year'],
                'cited_papers': cited_str
            })

def save_as_json(papers, filename):
    """Save papers data as JSON file."""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(papers, jsonfile, indent=2, ensure_ascii=False)

def generate_performance_test_data(num_papers=500):
    """Generate large dataset for performance testing."""
    print(f"Generating {num_papers} papers for performance testing...")
    papers = generate_citation_network(num_papers)
    return papers

def main():
    """Generate various test datasets."""
    print("Academic Knowledge Graph - Test Data Generator")
    print("=" * 50)
    
    # Generate citation network
    print("1. Generating citation network dataset...")
    citation_network = generate_citation_network(30)
    save_as_csv(citation_network, 'generated_citation_network.csv')
    save_as_json(citation_network, 'generated_citation_network.json')
    print(f"   Created: generated_citation_network.csv ({len(citation_network)} papers)")
    print(f"   Created: generated_citation_network.json ({len(citation_network)} papers)")
    
    # Generate research group data
    print("\n2. Generating research group dataset...")
    research_group = generate_research_group_data()
    save_as_csv(research_group, 'generated_research_group.csv')
    save_as_json(research_group, 'generated_research_group.json')
    print(f"   Created: generated_research_group.csv ({len(research_group)} papers)")
    print(f"   Created: generated_research_group.json ({len(research_group)} papers)")
    
    # Generate highly cited scenario
    print("\n3. Generating highly cited paper scenario...")
    highly_cited = generate_highly_cited_paper_scenario()
    save_as_csv(highly_cited, 'generated_highly_cited.csv')
    save_as_json(highly_cited, 'generated_highly_cited.json')
    print(f"   Created: generated_highly_cited.csv ({len(highly_cited)} papers)")
    print(f"   Created: generated_highly_cited.json ({len(highly_cited)} papers)")
    
    # Generate performance test data
    print("\n4. Generating performance test dataset...")
    performance_data = generate_performance_test_data(200)
    save_as_csv(performance_data, 'generated_performance_test.csv')
    print(f"   Created: generated_performance_test.csv ({len(performance_data)} papers)")
    
    print("\n" + "=" * 50)
    print("Data generation complete!")
    print("\nGenerated files:")
    print("- generated_citation_network.csv/json")
    print("- generated_research_group.csv/json") 
    print("- generated_highly_cited.csv/json")
    print("- generated_performance_test.csv")
    print("\nYou can now upload these files to test the Knowledge Graph application.")

if __name__ == "__main__":
    main() 