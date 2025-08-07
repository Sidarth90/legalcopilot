#!/usr/bin/env python3
"""
Fresh Legal Pain Points Scraper - 2024/2025 Current Issues
Focus on current AI tools and specific legal workflows
"""

import json
from reddit_scraper import reddit_client
from datetime import datetime, timedelta

def search_current_legal_pain_points():
    """Search for current legal pain points with updated keywords"""
    
    # Target subreddits
    subreddits = ['LawFirm', 'LegalAdvice', 'Paralegal', 'BigLaw', 'legal', 'ChatGPT', 'artificial']
    
    # Updated keywords focusing on current AI and specific legal tasks
    current_keywords = [
        # AI-specific legal tools
        'legal copilot',
        'ai contract review',
        'nda review',
        'contract ai',
        'legal ai tools',
        
        # Specific contract types
        'employment contract review',
        'service agreement',
        'lease review',
        'vendor contract',
        'partnership agreement',
        
        # Current AI tool limitations
        'ChatGPT legal',
        'Claude legal',
        'GPT-4 contracts',
        'AI hallucination legal',
        'legal ai accuracy',
        
        # Workflow-specific pain points
        'contract redlining',
        'legal markup',
        'contract negotiation',
        'legal document automation',
        'contract templates',
        
        # Time and cost pressures (recent)
        'legal billing pressure',
        'contract review time',
        'legal efficiency',
        'law firm profitability',
        'billable hours stress',
        
        # Recent technology adoption
        'legal tech stack',
        'law firm software',
        'legal workflow automation',
        'document review software',
        'contract management tool'
    ]
    
    all_results = {}
    
    for subreddit in subreddits:
        print(f"\n[INFO] Searching r/{subreddit} with current keywords...")
        subreddit_results = {}
        
        for keyword in current_keywords:
            print(f"  Searching for '{keyword}'...")
            try:
                # Search with time restriction - only posts from last 12 months
                posts = reddit_client.search_subreddit(subreddit, keyword, limit=20)
                
                if posts:
                    # Filter for recent posts (last 12 months)
                    recent_posts = []
                    cutoff_date = datetime.now() - timedelta(days=365)
                    
                    for post in posts:
                        post_date = datetime.strptime(post['created_utc'], '%Y-%m-%d %H:%M:%S')
                        if post_date > cutoff_date:
                            recent_posts.append(post)
                    
                    if recent_posts:
                        subreddit_results[keyword] = recent_posts
                        print(f"    Found {len(recent_posts)} recent posts (last 12 months)")
                    else:
                        print(f"    No recent posts found")
                else:
                    print(f"    No posts found")
            except Exception as e:
                print(f"    Error: {e}")
                continue
        
        if subreddit_results:
            all_results[subreddit] = subreddit_results
    
    return all_results

def extract_current_pain_points(results):
    """Extract and categorize current pain points"""
    
    pain_points = {
        'ai_tool_limitations': [],
        'specific_contract_challenges': [],
        'workflow_bottlenecks': [],
        'cost_time_pressures': [],
        'technology_adoption_issues': [],
        'accuracy_trust_concerns': []
    }
    
    # Updated keywords for categorization
    keywords = {
        'ai_tool_limitations': ['ChatGPT', 'Claude', 'GPT-4', 'AI hallucination', 'ai accuracy', 'legal ai'],
        'specific_contract_challenges': ['nda', 'employment contract', 'lease review', 'service agreement', 'vendor contract'],
        'workflow_bottlenecks': ['redlining', 'markup', 'negotiation', 'workflow', 'process', 'bottleneck'],
        'cost_time_pressures': ['billing', 'billable hours', 'time pressure', 'efficiency', 'profitability'],
        'technology_adoption_issues': ['tech stack', 'software', 'automation', 'tool', 'adoption'],
        'accuracy_trust_concerns': ['accuracy', 'trust', 'reliable', 'mistake', 'error', 'quality']
    }
    
    for subreddit, subreddit_data in results.items():
        for keyword, posts in subreddit_data.items():
            for post in posts:
                title_lower = post['title'].lower()
                content_lower = post.get('selftext', '').lower()
                combined_text = f"{title_lower} {content_lower}"
                
                # Categorize based on keywords
                for category, category_keywords in keywords.items():
                    if any(kw in combined_text for kw in category_keywords):
                        pain_point = {
                            'title': post['title'],
                            'content_preview': post.get('selftext', '')[:300],
                            'score': post['score'],
                            'comments': post['num_comments'],
                            'subreddit': subreddit,
                            'date': post['created_utc'],
                            'link': post['permalink'],
                            'search_keyword': keyword
                        }
                        pain_points[category].append(pain_point)
    
    # Remove duplicates and sort by engagement
    for category in pain_points:
        seen_titles = set()
        unique_points = []
        for point in pain_points[category]:
            if point['title'] not in seen_titles:
                unique_points.append(point)
                seen_titles.add(point['title'])
        
        # Sort by combined engagement (score + comments)
        pain_points[category] = sorted(
            unique_points, 
            key=lambda x: x['score'] + x['comments'], 
            reverse=True
        )[:8]  # Top 8 per category
    
    return pain_points

def generate_current_insights_report(pain_points):
    """Generate report focused on current, actionable insights"""
    
    report = []
    report.append("# Current Legal AI Pain Points Analysis (2024-2025)")
    report.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Recent posts only*\n")
    
    category_titles = {
        'ai_tool_limitations': '## Current AI Tool Limitations',
        'specific_contract_challenges': '## Specific Contract Type Challenges', 
        'workflow_bottlenecks': '## Workflow Bottlenecks',
        'cost_time_pressures': '## Cost & Time Pressures',
        'technology_adoption_issues': '## Technology Adoption Issues',
        'accuracy_trust_concerns': '## Accuracy & Trust Concerns'
    }
    
    total_insights = 0
    for category, title in category_titles.items():
        points = pain_points[category]
        if points:
            report.append(title)
            for i, point in enumerate(points[:5], 1):  # Top 5 per category
                report.append(f"\n**{i}. {point['title']}** ({point['date'][:10]})")
                report.append(f"- Source: r/{point['subreddit']} via '{point['search_keyword']}'")
                report.append(f"- Engagement: {point['score']} upvotes, {point['comments']} comments")
                if point['content_preview'].strip():
                    report.append(f"- Preview: *{point['content_preview'].strip()}...*")
                report.append(f"- [Link]({point['link']})")
                total_insights += 1
            report.append("")
        else:
            report.append(title)
            report.append("\n*No recent posts found in this category*\n")
    
    # Add summary
    report.insert(2, f"**Total Recent Insights Found: {total_insights}**\n")
    
    return "\n".join(report)

def main():
    """Main execution for current legal pain points research"""
    print("[INFO] Starting Fresh Legal Pain Points Research (2024-2025)...")
    print("Focusing on recent posts and current AI tool challenges...")
    
    # Search with current keywords
    results = search_current_legal_pain_points()
    
    # Extract and categorize
    print("\n[INFO] Analyzing current pain points...")
    pain_points = extract_current_pain_points(results)
    
    # Generate report
    report = generate_current_insights_report(pain_points)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(f'current_legal_pain_points_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump({
            'raw_results': results,
            'categorized_pain_points': pain_points,
            'generated_at': datetime.now().isoformat(),
            'keywords_used': 'Updated for 2024-2025 current issues'
        }, f, indent=2, ensure_ascii=False)
    
    with open(f'current_pain_points_report_{timestamp}.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[SUCCESS] Fresh research complete!")
    print(f"- Raw data: current_legal_pain_points_{timestamp}.json")
    print(f"- Report: current_pain_points_report_{timestamp}.md")
    
    # Summary
    categories_with_data = [k for k, v in pain_points.items() if v]
    print(f"\n[SUMMARY] Found current pain points in {len(categories_with_data)} categories:")
    
    for category, points in pain_points.items():
        if points:
            category_name = category.replace('_', ' ').title()
            print(f"- {category_name}: {len(points)} unique recent posts")

if __name__ == "__main__":
    main()