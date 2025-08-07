#!/usr/bin/env python3
"""
Legal Pain Points Scraper for Legal Copilot Research
Scrapes Reddit for contract review and legal workflow pain points
"""

import json
from reddit_scraper import reddit_client
from datetime import datetime

def search_legal_pain_points():
    """Search multiple legal subreddits for pain points related to contract review"""
    
    # Target subreddits and search terms
    subreddits = ['LawFirm', 'lawyers', 'LegalAdvice', 'Paralegal', 'BigLaw', 'legal']
    search_terms = [
        'contract review',
        'contract drafting', 
        'document review',
        'legal technology',
        'workflow problems',
        'pain points',
        'automation',
        'time consuming',
        'repetitive work',
        'billable hours',
        'inefficient'
    ]
    
    all_results = {}
    
    for subreddit in subreddits:
        print(f"\n[INFO] Searching r/{subreddit}...")
        subreddit_results = {}
        
        for term in search_terms:
            print(f"  Searching for '{term}'...")
            try:
                posts = reddit_client.search_subreddit(subreddit, term, limit=15)
                if posts:
                    subreddit_results[term] = posts
                    print(f"    Found {len(posts)} posts")
                else:
                    print(f"    No posts found")
            except Exception as e:
                print(f"    Error: {e}")
                continue
        
        all_results[subreddit] = subreddit_results
    
    return all_results

def extract_pain_points_from_results(results):
    """Extract key pain points from Reddit search results"""
    
    pain_points = {
        'contract_review_challenges': [],
        'workflow_inefficiencies': [],
        'technology_gaps': [],
        'time_management_issues': [],
        'client_pressure': [],
        'cost_concerns': []
    }
    
    # Keywords that indicate different types of pain points
    keywords = {
        'contract_review_challenges': ['contract review', 'redlining', 'clause', 'terms', 'negotiation', 'markup'],
        'workflow_inefficiencies': ['workflow', 'process', 'manual', 'repetitive', 'inefficient', 'bottleneck'],
        'technology_gaps': ['technology', 'software', 'automation', 'AI', 'tool', 'platform'],
        'time_management_issues': ['time', 'hours', 'deadline', 'rush', 'overtime', 'billable'],
        'client_pressure': ['client', 'pressure', 'expectation', 'turnaround', 'delivery'],
        'cost_concerns': ['cost', 'expensive', 'budget', 'fee', 'pricing', 'affordable']
    }
    
    for subreddit, subreddit_data in results.items():
        for term, posts in subreddit_data.items():
            for post in posts:
                title_lower = post['title'].lower()
                content_lower = post.get('selftext', '').lower()
                combined_text = f"{title_lower} {content_lower}"
                
                # Categorize based on keywords
                for category, category_keywords in keywords.items():
                    if any(keyword in combined_text for keyword in category_keywords):
                        pain_point = {
                            'title': post['title'],
                            'content_preview': post.get('selftext', '')[:200],
                            'score': post['score'],
                            'comments': post['num_comments'],
                            'subreddit': subreddit,
                            'date': post['created_utc'],
                            'link': post['permalink']
                        }
                        pain_points[category].append(pain_point)
    
    # Remove duplicates and sort by score
    for category in pain_points:
        # Remove duplicates based on title
        seen_titles = set()
        unique_points = []
        for point in pain_points[category]:
            if point['title'] not in seen_titles:
                unique_points.append(point)
                seen_titles.add(point['title'])
        
        # Sort by score (engagement) descending
        pain_points[category] = sorted(unique_points, key=lambda x: x['score'], reverse=True)[:10]
    
    return pain_points

def generate_pain_points_report(pain_points):
    """Generate a formatted report of pain points"""
    
    report = []
    report.append("# Reddit-Sourced Legal Pain Points Analysis")
    report.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    category_titles = {
        'contract_review_challenges': '## Contract Review Challenges',
        'workflow_inefficiencies': '## Workflow Inefficiencies', 
        'technology_gaps': '## Technology Gaps',
        'time_management_issues': '## Time Management Issues',
        'client_pressure': '## Client Pressure Points',
        'cost_concerns': '## Cost Concerns'
    }
    
    for category, title in category_titles.items():
        report.append(title)
        points = pain_points[category]
        
        if points:
            for i, point in enumerate(points[:5], 1):  # Top 5 per category
                report.append(f"\n**{i}. {point['title']}**")
                report.append(f"- Source: r/{point['subreddit']}")
                report.append(f"- Engagement: {point['score']} upvotes, {point['comments']} comments")
                report.append(f"- Date: {point['date']}")
                if point['content_preview'].strip():
                    report.append(f"- Preview: *{point['content_preview'].strip()}...*")
                report.append(f"- [Link]({point['link']})")
        else:
            report.append("\n*No specific pain points found in this category*")
        
        report.append("")
    
    return "\n".join(report)

def main():
    """Main execution function"""
    print("[INFO] Starting Legal Pain Points Research...")
    
    # Search for pain points
    results = search_legal_pain_points()
    
    # Extract and categorize pain points
    print("\n[INFO] Analyzing results...")
    pain_points = extract_pain_points_from_results(results)
    
    # Generate report
    report = generate_pain_points_report(pain_points)
    
    # Save results
    with open('reddit_legal_pain_points.json', 'w', encoding='utf-8') as f:
        json.dump({
            'raw_results': results,
            'categorized_pain_points': pain_points,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    with open('reddit_pain_points_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[SUCCESS] Research complete!")
    print(f"- Raw data saved to: reddit_legal_pain_points.json")
    print(f"- Report saved to: reddit_pain_points_report.md")
    print(f"\n[SUMMARY] Found pain points in {len([k for k, v in pain_points.items() if v])} categories")
    
    for category, points in pain_points.items():
        if points:
            print(f"- {category.replace('_', ' ').title()}: {len(points)} unique posts")

if __name__ == "__main__":
    main()