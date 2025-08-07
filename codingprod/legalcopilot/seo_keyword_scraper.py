#!/usr/bin/env python3
"""
SEO Keyword Scraper for Contract Explanation Services
Extract real search terms from Reddit posts and comments
"""

import json
from reddit_scraper import reddit_client
from collections import Counter
import re
from datetime import datetime

def extract_search_intent_keywords():
    """Extract keywords that indicate search intent for contract help"""
    
    # Target subreddits where people ask for contract help
    subreddits = ['LegalAdvice', 'smallbusiness', 'entrepreneur', 'personalfinance', 'freelance']
    
    # Search for posts where people are asking for help understanding contracts
    search_terms = [
        'help understand contract',
        'what does this contract mean',
        'contract confusing',
        'explain contract',
        'contract terms meaning',
        'contract clause meaning',
        'need help with contract',
        'contract review help',
        'contract advice',
        'understand lease',
        'employment contract help',
        'nda explanation',
        'service agreement help',
        'contract questions'
    ]
    
    all_posts = {}
    
    for subreddit in subreddits:
        print(f"\n[INFO] Extracting keywords from r/{subreddit}...")
        subreddit_posts = {}
        
        for term in search_terms:
            print(f"  Searching for '{term}'...")
            try:
                posts = reddit_client.search_subreddit(subreddit, term, limit=20)
                if posts:
                    subreddit_posts[term] = posts
                    print(f"    Found {len(posts)} posts")
            except Exception as e:
                print(f"    Error: {e}")
                continue
        
        if subreddit_posts:
            all_posts[subreddit] = subreddit_posts
    
    return all_posts

def analyze_title_keywords(posts_data):
    """Analyze post titles to extract common keywords and phrases"""
    
    all_titles = []
    keyword_phrases = []
    
    for subreddit, subreddit_data in posts_data.items():
        for term, posts in subreddit_data.items():
            for post in posts:
                title = post['title'].lower()
                all_titles.append(title)
                
                # Extract key phrases that indicate search intent
                patterns = [
                    r'help.*?understand.*?contract',
                    r'what does.*?mean',
                    r'explain.*?contract',
                    r'contract.*?confusing',
                    r'need help.*?contract',
                    r'contract.*?advice',
                    r'understand.*?lease',
                    r'employment contract',
                    r'service agreement',
                    r'nda.*?review',
                    r'contract.*?terms',
                    r'legal.*?help'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, title)
                    keyword_phrases.extend(matches)
    
    # Count word frequency in titles
    words = []
    for title in all_titles:
        # Clean and tokenize
        clean_title = re.sub(r'[^\w\s]', ' ', title)
        title_words = clean_title.split()
        # Filter out common stop words and keep relevant terms
        relevant_words = [word for word in title_words if len(word) > 3 and 
                         word not in ['this', 'that', 'with', 'have', 'they', 'from', 'what', 'when', 'where']]
        words.extend(relevant_words)
    
    return Counter(words), keyword_phrases

def extract_seo_keywords(posts_data):
    """Extract potential SEO keywords from the data"""
    
    word_counts, phrases = analyze_title_keywords(posts_data)
    
    # Contract-related high-frequency words
    contract_keywords = {}
    legal_keywords = {}
    action_keywords = {}
    
    for word, count in word_counts.most_common(100):
        if any(term in word for term in ['contract', 'agreement', 'lease', 'employment']):
            contract_keywords[word] = count
        elif any(term in word for term in ['legal', 'lawyer', 'attorney', 'law']):
            legal_keywords[word] = count
        elif any(term in word for term in ['help', 'explain', 'understand', 'review', 'advice']):
            action_keywords[word] = count
    
    return {
        'contract_terms': contract_keywords,
        'legal_terms': legal_keywords, 
        'action_terms': action_keywords,
        'common_phrases': phrases,
        'top_words': dict(word_counts.most_common(30))
    }

def generate_domain_suggestions(keyword_data):
    """Generate domain name suggestions based on keyword analysis"""
    
    # Most common contract-related terms
    contract_terms = ['contract', 'agreement', 'legal', 'document']
    action_terms = ['explain', 'help', 'understand', 'review', 'simple', 'plain']
    
    domain_suggestions = []
    
    # Combine high-frequency terms
    for action in action_terms:
        for contract in contract_terms:
            suggestions = [
                f"{action}{contract}.com",
                f"{contract}{action}.com", 
                f"{action}my{contract}.com",
                f"{contract}{action}er.com"
            ]
            domain_suggestions.extend(suggestions)
    
    # Add specific combinations based on keyword data
    top_combinations = [
        'contracthelp.com',
        'explaincontract.com', 
        'contractsimple.com',
        'plaincontract.com',
        'contractexplainer.com',
        'understandcontract.com',
        'contractadvice.com',
        'simplecontract.com',
        'contractguru.com',
        'contractcoach.com',
        'easycontract.com',
        'contractfriend.com'
    ]
    
    domain_suggestions.extend(top_combinations)
    
    return list(set(domain_suggestions))  # Remove duplicates

def generate_seo_report(keyword_data, domain_suggestions):
    """Generate a comprehensive SEO report"""
    
    report = []
    report.append("# SEO Keyword Analysis for Contract Explanation Service")
    report.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    report.append("## Top Contract-Related Keywords")
    for word, count in list(keyword_data['contract_terms'].items())[:10]:
        report.append(f"- **{word}:** {count} mentions")
    
    report.append("\n## Top Action Keywords (Search Intent)")  
    for word, count in list(keyword_data['action_terms'].items())[:10]:
        report.append(f"- **{word}:** {count} mentions")
    
    report.append("\n## Most Frequent Words Overall")
    for word, count in list(keyword_data['top_words'].items())[:15]:
        report.append(f"- **{word}:** {count} mentions")
    
    report.append("\n## Domain Name Suggestions (SEO Optimized)")
    report.append("### Primary Recommendations:")
    for domain in domain_suggestions[:10]:
        report.append(f"- {domain}")
    
    report.append("\n### Alternative Options:")
    for domain in domain_suggestions[10:20]:
        report.append(f"- {domain}")
    
    report.append("\n## SEO Strategy Insights")
    report.append("### Target Keywords for Content:")
    
    # Generate content keywords based on analysis
    content_keywords = [
        "contract explanation",
        "understand my contract", 
        "contract help",
        "explain contract terms",
        "contract review service",
        "simple contract explanation",
        "contract advice",
        "legal document help",
        "contract meaning",
        "what does my contract mean"
    ]
    
    for keyword in content_keywords:
        report.append(f"- \"{keyword}\"")
    
    report.append("\n### Long-tail Keywords for Blog Content:")
    longtail_keywords = [
        "how to understand employment contract",
        "what does this contract clause mean", 
        "get help understanding lease agreement",
        "free contract explanation service",
        "simple contract review online",
        "contract terms explained in plain english",
        "help me understand my service agreement"
    ]
    
    for keyword in longtail_keywords:
        report.append(f"- \"{keyword}\"")
    
    return "\n".join(report)

def main():
    """Main execution for SEO keyword analysis"""
    print("[INFO] Starting SEO keyword extraction from Reddit...")
    
    # Extract posts with search intent
    posts_data = extract_search_intent_keywords()
    
    # Analyze keywords
    print("\n[INFO] Analyzing keywords and search intent...")
    keyword_data = extract_seo_keywords(posts_data)
    
    # Generate domain suggestions  
    print("\n[INFO] Generating domain suggestions...")
    domain_suggestions = generate_domain_suggestions(keyword_data)
    
    # Generate comprehensive report
    report = generate_seo_report(keyword_data, domain_suggestions)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(f'seo_keyword_analysis_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump({
            'posts_data': posts_data,
            'keyword_analysis': keyword_data,
            'domain_suggestions': domain_suggestions,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    with open(f'seo_report_{timestamp}.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[SUCCESS] SEO analysis complete!")
    print(f"- Data: seo_keyword_analysis_{timestamp}.json")
    print(f"- Report: seo_report_{timestamp}.md")
    
    # Display top findings
    print(f"\n[SUMMARY] Top SEO Insights:")
    print("Top contract keywords:", list(keyword_data['contract_terms'].keys())[:5])
    print("Top action keywords:", list(keyword_data['action_terms'].keys())[:5])  
    print("Recommended domains:", domain_suggestions[:5])

if __name__ == "__main__":
    main()