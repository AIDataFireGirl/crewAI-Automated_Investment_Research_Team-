"""
News Gathering Agent
Collects financial news from multiple sources and filters relevant information.
"""

import os
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from config.security import security_manager, rate_limit_decorator, input_validation_decorator

class NewsGathererAgent:
    """Agent responsible for gathering financial news from various sources."""
    
    def __init__(self):
        """Initialize the news gatherer agent with API clients and configuration."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize News API client
        self.news_api_key = os.getenv('NEWS_API_KEY')
        if self.news_api_key and security_manager.validate_api_key(self.news_api_key, 'news'):
            self.news_client = NewsApiClient(api_key=self.news_api_key)
        else:
            self.news_client = None
            self.logger.warning("News API key not configured or invalid")
        
        # Define financial news sources
        self.financial_sources = [
            'reuters', 'bloomberg', 'cnbc', 'marketwatch', 
            'yahoo-finance', 'seeking-alpha', 'investing.com'
        ]
        
        # Keywords for financial news filtering
        self.financial_keywords = [
            'earnings', 'revenue', 'profit', 'loss', 'stock', 'market',
            'trading', 'investment', 'finance', 'economy', 'GDP',
            'inflation', 'interest rates', 'Federal Reserve', 'SEC'
        ]
        
        # Rate limiting configuration
        self.request_delay = 1  # seconds between requests
        self.max_articles_per_source = 10
        
    @rate_limit_decorator
    @input_validation_decorator
    def gather_financial_news(self, ticker_symbol: str = None, 
                            keywords: List[str] = None, 
                            days_back: int = 7) -> Dict[str, Any]:
        """
        Gather financial news from multiple sources.
        
        Args:
            ticker_symbol: Stock ticker symbol to search for
            keywords: Additional keywords to search for
            days_back: Number of days to look back for news
            
        Returns:
            Dict containing gathered news articles and metadata
        """
        try:
            self.logger.info(f"Starting news gathering for ticker: {ticker_symbol}")
            
            # Validate ticker symbol if provided
            if ticker_symbol and not security_manager.validate_ticker_symbol(ticker_symbol):
                raise ValueError(f"Invalid ticker symbol: {ticker_symbol}")
            
            # Combine keywords
            search_keywords = keywords or []
            if ticker_symbol:
                search_keywords.append(ticker_symbol)
            search_keywords.extend(self.financial_keywords)
            
            # Gather news from different sources
            news_data = {
                'ticker_symbol': ticker_symbol,
                'search_keywords': search_keywords,
                'gathered_at': datetime.now().isoformat(),
                'articles': [],
                'sources': [],
                'summary': {}
            }
            
            # Gather from News API
            if self.news_client:
                news_data['articles'].extend(
                    self._gather_from_news_api(search_keywords, days_back)
                )
            
            # Gather from additional sources
            news_data['articles'].extend(
                self._gather_from_additional_sources(search_keywords, days_back)
            )
            
            # Process and filter articles
            processed_articles = self._process_articles(news_data['articles'])
            news_data['articles'] = processed_articles
            
            # Generate summary
            news_data['summary'] = self._generate_news_summary(processed_articles)
            
            self.logger.info(f"Successfully gathered {len(processed_articles)} articles")
            return news_data
            
        except Exception as e:
            self.logger.error(f"Error gathering news: {str(e)}")
            security_manager.log_security_event("news_gathering_error", {
                'error': str(e),
                'ticker': ticker_symbol
            })
            raise
    
    def _gather_from_news_api(self, keywords: List[str], days_back: int) -> List[Dict]:
        """Gather news from News API."""
        articles = []
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Search for each keyword
            for keyword in keywords[:5]:  # Limit to 5 keywords to avoid rate limits
                try:
                    response = self.news_client.get_everything(
                        q=keyword,
                        from_param=start_date.strftime('%Y-%m-%d'),
                        to=end_date.strftime('%Y-%m-%d'),
                        language='en',
                        sort_by='relevancy',
                        page_size=min(self.max_articles_per_source, 20)
                    )
                    
                    for article in response.get('articles', []):
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'content': article.get('content', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'published_at': article.get('publishedAt', ''),
                            'keyword_matched': keyword,
                            'relevance_score': self._calculate_relevance_score(article, keyword)
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Error fetching news for keyword '{keyword}': {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error with News API: {str(e)}")
        
        return articles
    
    def _gather_from_additional_sources(self, keywords: List[str], days_back: int) -> List[Dict]:
        """Gather news from additional sources (placeholder for future implementation)."""
        # This method can be extended to gather from other sources
        # like RSS feeds, web scraping, etc.
        return []
    
    def _calculate_relevance_score(self, article: Dict, keyword: str) -> float:
        """Calculate relevance score for an article based on keyword matching."""
        score = 0.0
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = article.get('content', '').lower()
        
        # Keyword in title gets highest score
        if keyword.lower() in title:
            score += 3.0
        
        # Keyword in description gets medium score
        if keyword.lower() in description:
            score += 2.0
        
        # Keyword in content gets lower score
        if keyword.lower() in content:
            score += 1.0
        
        # Financial keywords boost score
        for fin_keyword in self.financial_keywords:
            if fin_keyword.lower() in title or fin_keyword.lower() in description:
                score += 0.5
        
        return min(score, 5.0)  # Cap at 5.0
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process and filter articles for relevance and quality."""
        processed = []
        
        for article in articles:
            # Filter out articles with low relevance
            if article.get('relevance_score', 0) < 1.0:
                continue
            
            # Remove duplicate articles based on title similarity
            if not self._is_duplicate(article, processed):
                processed.append(article)
        
        # Sort by relevance score
        processed.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return processed[:50]  # Limit to top 50 articles
    
    def _is_duplicate(self, article: Dict, existing_articles: List[Dict]) -> bool:
        """Check if article is a duplicate based on title similarity."""
        title = article.get('title', '').lower()
        
        for existing in existing_articles:
            existing_title = existing.get('title', '').lower()
            
            # Simple similarity check (can be improved with more sophisticated algorithms)
            if title == existing_title or title in existing_title or existing_title in title:
                return True
        
        return False
    
    def _generate_news_summary(self, articles: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for gathered news."""
        if not articles:
            return {
                'total_articles': 0,
                'top_sources': [],
                'top_keywords': [],
                'sentiment_overview': 'neutral'
            }
        
        # Count sources
        source_counts = {}
        keyword_counts = {}
        
        for article in articles:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
            
            keyword = article.get('keyword_matched', '')
            if keyword:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Get top sources and keywords
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_articles': len(articles),
            'top_sources': top_sources,
            'top_keywords': top_keywords,
            'average_relevance_score': sum(a.get('relevance_score', 0) for a in articles) / len(articles),
            'date_range': {
                'earliest': min(a.get('published_at', '') for a in articles if a.get('published_at')),
                'latest': max(a.get('published_at', '') for a in articles if a.get('published_at'))
            }
        }
    
    def get_news_for_ticker(self, ticker_symbol: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Get news specifically for a ticker symbol.
        
        Args:
            ticker_symbol: Stock ticker symbol
            days_back: Number of days to look back
            
        Returns:
            Dict containing ticker-specific news
        """
        return self.gather_financial_news(
            ticker_symbol=ticker_symbol,
            days_back=days_back
        )
    
    def get_market_overview(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Get general market overview news.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dict containing market overview news
        """
        return self.gather_financial_news(
            keywords=['market', 'economy', 'trading', 'investing'],
            days_back=days_back
        ) 