#!/usr/bin/env python3
"""
Reddit API integration for Claude Code
Author: Sidarth Radjou
"""

import praw
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

class RedditClient:
    """Reddit API client for Claude Code"""
    
    def __init__(self):
        """Initialize Reddit client with credentials"""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
    def test_connection(self) -> bool:
        """Test if Reddit API connection works"""
        try:
            # Try to access a public subreddit
            subreddit = self.reddit.subreddit('python')
            _ = subreddit.display_name
            print("[SUCCESS] Reddit API connection successful!")
            return True
        except Exception as e:
            print(f"[ERROR] Reddit API connection failed: {e}")
            return False
    
    def get_subreddit_posts(self, subreddit_name: str, limit: int = 10, sort: str = 'hot') -> List[Dict[str, Any]]:
        """
        Get posts from a subreddit
        
        Args:
            subreddit_name: Name of subreddit (without r/)
            limit: Number of posts to fetch
            sort: 'hot', 'new', 'top', 'rising'
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Choose sorting method
            if sort == 'hot':
                posts = subreddit.hot(limit=limit)
            elif sort == 'new':
                posts = subreddit.new(limit=limit)
            elif sort == 'top':
                posts = subreddit.top(limit=limit)
            elif sort == 'rising':
                posts = subreddit.rising(limit=limit)
            else:
                posts = subreddit.hot(limit=limit)
            
            posts_data = []
            for post in posts:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'author': str(post.author) if post.author else '[deleted]',
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                    'url': post.url,
                    'permalink': f"https://reddit.com{post.permalink}",
                    'selftext': post.selftext,
                    'is_self': post.is_self,
                    'subreddit': str(post.subreddit),
                    'flair': post.link_flair_text,
                    'over_18': post.over_18
                }
                posts_data.append(post_data)
            
            return posts_data
            
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    def search_subreddit(self, subreddit_name: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search within a specific subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            search_results = []
            
            for post in subreddit.search(query, limit=limit):
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'author': str(post.author) if post.author else '[deleted]',
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                    'permalink': f"https://reddit.com{post.permalink}",
                    'selftext': post.selftext[:300] + '...' if len(post.selftext) > 300 else post.selftext
                }
                search_results.append(post_data)
            
            return search_results
            
        except Exception as e:
            print(f"Error searching r/{subreddit_name} for '{query}': {e}")
            return []
    
    def get_post_comments(self, post_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get comments from a specific post"""
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            comments_data = []
            comment_count = 0
            
            for comment in submission.comments:
                if comment_count >= limit:
                    break
                    
                if hasattr(comment, 'body'):
                    comment_data = {
                        'id': comment.id,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'permalink': f"https://reddit.com{comment.permalink}"
                    }
                    comments_data.append(comment_data)
                    comment_count += 1
            
            return comments_data
            
        except Exception as e:
            print(f"Error fetching comments for post {post_id}: {e}")
            return []
    
    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """Get basic information about a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            return {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.description,
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                'over_18': subreddit.over18,
                'public_description': subreddit.public_description
            }
            
        except Exception as e:
            print(f"Error getting info for r/{subreddit_name}: {e}")
            return {}

# Initialize the client
reddit_client = RedditClient()

def main():
    """Example usage and testing"""
    print("[INFO] Testing Reddit API connection...")
    
    if not reddit_client.test_connection():
        return
    
    print("\n[INFO] Getting posts from r/LawFirm...")
    posts = reddit_client.get_subreddit_posts('LawFirm', limit=5)
    
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Author: {post['author']} | Score: {post['score']} | Comments: {post['num_comments']} | Date: {post['created_utc']}")
        if post['selftext']:
            preview = post['selftext'][:100].replace('\n', ' ')
            print(f"   Content: {preview}...")
        print(f"   Link: {post['permalink']}")
    
    print("\n[INFO] Searching for 'associate' in r/LawFirm...")
    search_results = reddit_client.search_subreddit('LawFirm', 'associate', limit=3)
    
    for i, post in enumerate(search_results, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Score: {post['score']} | Comments: {post['num_comments']}")

if __name__ == "__main__":
    main()

# Export the client for use in Claude Code
__all__ = ['reddit_client', 'RedditClient']