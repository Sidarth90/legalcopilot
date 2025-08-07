#!/usr/bin/env python3
"""
Research PDF.js text highlighting and coordinate mapping issues
Using existing Reddit scraper + web scraping for StackOverflow
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from reddit_scraper import reddit_client
from datetime import datetime

class PDFHighlightingResearcher:
    def __init__(self):
        self.reddit_client = reddit_client
        self.results = {
            'reddit_posts': [],
            'stackoverflow_posts': [],
            'github_issues': [],
            'timestamp': datetime.now().isoformat()
        }
    
    def search_reddit(self):
        """Search Reddit for PDF.js highlighting issues"""
        print("[INFO] Searching Reddit for PDF.js highlighting issues...")
        
        # Search queries related to our problem
        queries = [
            "pdf.js text highlighting coordinates",
            "pdf.js text layer coordinates mismatch",  
            "pdf.js highlight text programmatically",
            "pdf.js text selection coordinates wrong",
            "pdf.js coordinate mapping text overlay"
        ]
        
        # Relevant subreddits
        subreddits = ['webdev', 'javascript', 'programming', 'reactjs', 'Frontend']
        
        for subreddit in subreddits:
            for query in queries:
                try:
                    print(f"  Searching r/{subreddit} for: {query}")
                    results = self.reddit_client.search_subreddit(subreddit, query, limit=5)
                    
                    for post in results:
                        # Add source info
                        post['source'] = 'reddit'
                        post['subreddit'] = subreddit
                        post['search_query'] = query
                        self.results['reddit_posts'].append(post)
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"    Error searching r/{subreddit}: {e}")
                    continue
        
        print(f"[SUCCESS] Found {len(self.results['reddit_posts'])} Reddit posts")
    
    def search_stackoverflow(self):
        """Search StackOverflow for PDF.js highlighting issues"""
        print("[INFO] Searching StackOverflow...")
        
        # StackOverflow search queries
        queries = [
            "pdf.js text highlighting coordinates",
            "pdf.js text layer coordinate mapping",
            "pdf.js highlight text position wrong",
            "pdf.js getTextContent coordinates",
            "pdf.js text overlay positioning"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for query in queries:
            try:
                print(f"  Searching StackOverflow for: {query}")
                
                # Use StackOverflow search URL
                search_url = f"https://stackoverflow.com/search?q={query.replace(' ', '+')}"
                response = requests.get(search_url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find question results
                    questions = soup.find_all('div', class_='s-post-summary')
                    
                    for question in questions[:5]:  # Limit to top 5 per query
                        try:
                            title_elem = question.find('h3').find('a')
                            title = title_elem.text.strip() if title_elem else 'No title'
                            url = 'https://stackoverflow.com' + title_elem.get('href', '') if title_elem else ''
                            
                            # Get question stats
                            stats = question.find('div', class_='s-post-summary--stats')
                            votes = stats.find('span', class_='s-post-summary--stats-item-number') if stats else None
                            votes = votes.text.strip() if votes else '0'
                            
                            # Get excerpt
                            excerpt_elem = question.find('div', class_='s-post-summary--content-excerpt')
                            excerpt = excerpt_elem.text.strip() if excerpt_elem else 'No excerpt'
                            
                            post_data = {
                                'title': title,
                                'url': url,
                                'votes': votes,
                                'excerpt': excerpt,
                                'source': 'stackoverflow',
                                'search_query': query
                            }
                            
                            self.results['stackoverflow_posts'].append(post_data)
                            
                        except Exception as e:
                            print(f"    Error parsing question: {e}")
                            continue
                
                time.sleep(2)  # Rate limiting for StackOverflow
                
            except Exception as e:
                print(f"  Error searching StackOverflow for '{query}': {e}")
                continue
        
        print(f"[SUCCESS] Found {len(self.results['stackoverflow_posts'])} StackOverflow posts")
    
    def search_github_issues(self):
        """Search GitHub issues for PDF.js highlighting problems"""
        print("[INFO] Searching GitHub issues...")
        
        queries = [
            "text highlighting coordinates",
            "text layer coordinate mapping", 
            "highlight position wrong",
            "text overlay positioning",
            "getTextContent coordinates"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        for query in queries:
            try:
                print(f"  Searching GitHub for: {query}")
                
                # Search GitHub issues API
                search_url = f"https://api.github.com/search/issues?q={query.replace(' ', '+')}+repo:mozilla/pdf.js"
                response = requests.get(search_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', [])[:5]:  # Top 5 per query
                        issue_data = {
                            'title': item.get('title', 'No title'),
                            'url': item.get('html_url', ''),
                            'state': item.get('state', 'unknown'),
                            'comments': item.get('comments', 0),
                            'created_at': item.get('created_at', ''),
                            'body': item.get('body', '')[:300] + '...' if item.get('body') else 'No body',
                            'source': 'github',
                            'search_query': query
                        }
                        
                        self.results['github_issues'].append(issue_data)
                
                time.sleep(1)  # Rate limiting for GitHub API
                
            except Exception as e:
                print(f"  Error searching GitHub for '{query}': {e}")
                continue
        
        print(f"[SUCCESS] Found {len(self.results['github_issues'])} GitHub issues")
    
    def save_results(self, filename='pdf_highlighting_research.json'):
        """Save all research results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Results saved to {filename}")
        return filename
    
    def analyze_findings(self):
        """Analyze and summarize the findings"""
        print("\n" + "="*60)
        print("RESEARCH ANALYSIS SUMMARY")
        print("="*60)
        
        total_reddit = len(self.results['reddit_posts'])
        total_stackoverflow = len(self.results['stackoverflow_posts'])
        total_github = len(self.results['github_issues'])
        
        print(f"Reddit Posts Found: {total_reddit}")
        print(f"StackOverflow Posts Found: {total_stackoverflow}")  
        print(f"GitHub Issues Found: {total_github}")
        print(f"Total Sources: {total_reddit + total_stackoverflow + total_github}")
        
        print("\n" + "-"*40)
        print("TOP STACKOVERFLOW RESULTS:")
        print("-"*40)
        
        # Show top StackOverflow results
        top_so = sorted(self.results['stackoverflow_posts'], 
                       key=lambda x: int(x['votes'].replace(',', '') if x['votes'].isdigit() else 0), 
                       reverse=True)[:5]
        
        for i, post in enumerate(top_so, 1):
            print(f"{i}. {post['title']}")
            print(f"   Votes: {post['votes']} | URL: {post['url']}")
            print(f"   Excerpt: {post['excerpt'][:100]}...")
            print()
        
        print("-"*40)
        print("TOP GITHUB ISSUES:")
        print("-"*40)
        
        # Show top GitHub issues
        top_github = sorted(self.results['github_issues'], 
                           key=lambda x: x['comments'], 
                           reverse=True)[:5]
        
        for i, issue in enumerate(top_github, 1):
            print(f"{i}. {issue['title']}")
            print(f"   State: {issue['state']} | Comments: {issue['comments']}")
            print(f"   URL: {issue['url']}")
            print(f"   Body: {issue['body'][:100]}...")
            print()

def main():
    """Run the research"""
    print("Starting PDF.js Text Highlighting Research...")
    print("="*60)
    
    researcher = PDFHighlightingResearcher()
    
    # Test Reddit connection first
    if not researcher.reddit_client.test_connection():
        print("[ERROR] Reddit API connection failed. Check credentials in .env file")
        return
    
    # Run searches
    researcher.search_reddit()
    researcher.search_stackoverflow() 
    researcher.search_github_issues()
    
    # Save and analyze
    filename = researcher.save_results()
    researcher.analyze_findings()
    
    print(f"\n[SUCCESS] Research complete! Results saved to {filename}")
    
    return researcher.results

if __name__ == "__main__":
    results = main()