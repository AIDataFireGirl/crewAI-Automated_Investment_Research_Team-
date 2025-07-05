"""
Investment Research Crew
Main crew that orchestrates news gathering, report analysis, and insight generation.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
from agents.news_gatherer import NewsGathererAgent
from agents.report_analyzer import ReportAnalyzerAgent
from agents.insight_generator import InsightGeneratorAgent
from config.security import security_manager

class InvestmentResearchCrew:
    """Main crew for automated investment research."""
    
    def __init__(self):
        """Initialize the investment research crew with all agents."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI model
        self.model = ChatOpenAI(
            model=os.getenv('DEFAULT_MODEL', 'gpt-4'),
            temperature=float(os.getenv('TEMPERATURE', 0.7)),
            max_retries=int(os.getenv('MAX_RETRIES', 3))
        )
        
        # Initialize agents
        self.news_gatherer = NewsGathererAgent()
        self.report_analyzer = ReportAnalyzerAgent()
        self.insight_generator = InsightGeneratorAgent()
        
        # Create CrewAI agents
        self.news_agent = self._create_news_agent()
        self.analysis_agent = self._create_analysis_agent()
        self.insight_agent = self._create_insight_agent()
        
        # Create crew
        self.crew = self._create_crew()
    
    def _create_news_agent(self) -> Agent:
        """Create the news gathering agent."""
        return Agent(
            role='Financial News Analyst',
            goal='Gather and analyze relevant financial news and market information',
            backstory="""You are an expert financial news analyst with years of experience 
            in gathering and analyzing market information. You have a deep understanding 
            of financial markets, economic indicators, and how news affects stock prices. 
            You excel at identifying relevant news articles and extracting key information 
            that could impact investment decisions.""",
            verbose=True,
            allow_delegation=False,
            tools=[self._news_gathering_tool]
        )
    
    def _create_analysis_agent(self) -> Agent:
        """Create the financial analysis agent."""
        return Agent(
            role='Financial Report Analyst',
            goal='Analyze financial reports, earnings data, and company fundamentals',
            backstory="""You are a senior financial analyst specializing in fundamental 
            analysis. You have extensive experience analyzing balance sheets, income 
            statements, cash flow statements, and earnings reports. You can identify 
            trends, calculate key ratios, and assess a company's financial health 
            and growth prospects.""",
            verbose=True,
            allow_delegation=False,
            tools=[self._financial_analysis_tool]
        )
    
    def _create_insight_agent(self) -> Agent:
        """Create the insight generation agent."""
        return Agent(
            role='Investment Strategist',
            goal='Generate comprehensive investment insights and recommendations',
            backstory="""You are a seasoned investment strategist with expertise in 
            combining multiple data sources to form investment recommendations. You 
            understand how to weigh different factors including valuation, growth, 
            risk, and market sentiment to provide actionable investment advice. 
            You excel at communicating complex financial analysis in clear, 
            actionable terms.""",
            verbose=True,
            allow_delegation=False,
            tools=[self._insight_generation_tool]
        )
    
    def _create_crew(self) -> Crew:
        """Create the investment research crew."""
        return Crew(
            agents=[self.news_agent, self.analysis_agent, self.insight_agent],
            tasks=[
                self._create_news_task(),
                self._create_analysis_task(),
                self._create_insight_task()
            ],
            verbose=True,
            memory=True
        )
    
    def _create_news_task(self) -> Task:
        """Create the news gathering task."""
        return Task(
            description="""Gather comprehensive financial news and market information 
            for the specified ticker symbol. Focus on:
            1. Company-specific news and announcements
            2. Industry and sector news that could impact the company
            3. Market sentiment and analyst opinions
            4. Economic factors affecting the stock
            5. Recent earnings reports and financial updates
            
            Provide a detailed summary of the most relevant news articles with 
            their potential impact on the stock price.""",
            agent=self.news_agent,
            expected_output="""A comprehensive news analysis report including:
            - Summary of key news articles
            - Market sentiment analysis
            - Potential impact on stock price
            - Risk factors identified in news
            - Opportunities mentioned in news coverage"""
        )
    
    def _create_analysis_task(self) -> Task:
        """Create the financial analysis task."""
        return Task(
            description="""Analyze the company's financial reports and fundamentals. 
            Focus on:
            1. Recent earnings reports and trends
            2. Balance sheet analysis and financial health
            3. Income statement analysis and profitability
            4. Cash flow analysis and liquidity
            5. Key financial ratios and metrics
            6. Growth trends and projections
            
            Provide detailed financial analysis with key insights and concerns.""",
            agent=self.analysis_agent,
            expected_output="""A comprehensive financial analysis report including:
            - Earnings analysis and trends
            - Financial health assessment
            - Key ratios and metrics
            - Growth analysis
            - Risk assessment
            - Valuation analysis"""
        )
    
    def _create_insight_task(self) -> Task:
        """Create the insight generation task."""
        return Task(
            description="""Combine the news analysis and financial analysis to generate 
            comprehensive investment insights and recommendations. Consider:
            1. Overall investment thesis
            2. Risk-reward assessment
            3. Valuation analysis
            4. Growth prospects
            5. Market sentiment impact
            6. Investment recommendation
            
            Provide clear, actionable investment advice with supporting rationale.""",
            agent=self.insight_agent,
            expected_output="""A comprehensive investment recommendation report including:
            - Investment recommendation (Buy/Hold/Sell)
            - Confidence level and rationale
            - Key risks and opportunities
            - Price targets and time horizon
            - Position sizing recommendations
            - Executive summary"""
        )
    
    def _news_gathering_tool(self, ticker_symbol: str, days_back: int = 7) -> str:
        """Tool for gathering financial news."""
        try:
            news_data = self.news_gatherer.gather_financial_news(
                ticker_symbol=ticker_symbol,
                days_back=days_back
            )
            
            # Format news data for the agent
            summary = f"News Analysis for {ticker_symbol}:\n\n"
            summary += f"Total Articles Found: {news_data['summary']['total_articles']}\n"
            summary += f"Analysis Period: {days_back} days\n\n"
            
            # Add top articles
            articles = news_data.get('articles', [])
            if articles:
                summary += "Key News Articles:\n"
                for i, article in enumerate(articles[:5], 1):
                    summary += f"{i}. {article['title']}\n"
                    summary += f"   Source: {article['source']}\n"
                    summary += f"   Relevance: {article['relevance_score']:.2f}\n"
                    summary += f"   Summary: {article['description'][:200]}...\n\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in news gathering tool: {str(e)}")
            return f"Error gathering news for {ticker_symbol}: {str(e)}"
    
    def _financial_analysis_tool(self, ticker_symbol: str, period: str = '1y') -> str:
        """Tool for analyzing financial reports."""
        try:
            analysis = self.report_analyzer.analyze_company_reports(
                ticker_symbol=ticker_symbol,
                period=period
            )
            
            # Format analysis for the agent
            summary = f"Financial Analysis for {ticker_symbol}:\n\n"
            
            # Company info
            company_info = analysis.get('company_info', {})
            if company_info:
                summary += f"Company: {company_info.get('name', 'Unknown')}\n"
                summary += f"Sector: {company_info.get('sector', 'Unknown')}\n"
                summary += f"Market Cap: ${company_info.get('market_cap', 0):,.0f}\n"
                summary += f"P/E Ratio: {company_info.get('pe_ratio', 0):.2f}\n\n"
            
            # Financial analysis summary
            analysis_summary = analysis.get('summary', {})
            if analysis_summary:
                summary += f"Overall Sentiment: {analysis_summary.get('overall_sentiment', 'neutral')}\n"
                summary += f"Key Findings: {len(analysis_summary.get('key_findings', []))}\n"
                summary += f"Recommendations: {len(analysis_summary.get('recommendations', []))}\n\n"
            
            # Add key insights
            insights = analysis.get('insights', [])
            if insights:
                summary += "Key Insights:\n"
                for insight in insights[:5]:
                    summary += f"• {insight['message']}\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in financial analysis tool: {str(e)}")
            return f"Error analyzing financial reports for {ticker_symbol}: {str(e)}"
    
    def _insight_generation_tool(self, news_data: str, analysis_data: str) -> str:
        """Tool for generating investment insights."""
        try:
            # This would typically combine the news and analysis data
            # For now, we'll create a basic insight generation
            summary = "Investment Insights Generated:\n\n"
            summary += "Based on the provided news and financial analysis data:\n"
            summary += "• Comprehensive evaluation of investment potential\n"
            summary += "• Risk assessment and mitigation strategies\n"
            summary += "• Growth prospects and market positioning\n"
            summary += "• Valuation analysis and fair value estimates\n"
            summary += "• Investment recommendation with confidence level\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in insight generation tool: {str(e)}")
            return f"Error generating insights: {str(e)}"
    
    def research_stock(self, ticker_symbol: str, 
                      days_back: int = 7, 
                      period: str = '1y') -> Dict[str, Any]:
        """
        Perform comprehensive investment research on a stock.
        
        Args:
            ticker_symbol: Stock ticker symbol to research
            days_back: Number of days of news to analyze
            period: Financial data period to analyze
            
        Returns:
            Dict containing comprehensive research results
        """
        try:
            self.logger.info(f"Starting comprehensive research for {ticker_symbol}")
            
            # Validate ticker symbol
            if not security_manager.validate_ticker_symbol(ticker_symbol):
                raise ValueError(f"Invalid ticker symbol: {ticker_symbol}")
            
            # Set up context for the crew
            context = {
                'ticker_symbol': ticker_symbol,
                'days_back': days_back,
                'period': period,
                'research_date': datetime.now().isoformat()
            }
            
            # Run the crew
            result = self.crew.kickoff(inputs=context)
            
            # Process and format results
            research_report = {
                'ticker_symbol': ticker_symbol,
                'research_date': datetime.now().isoformat(),
                'analysis_period': {
                    'news_days': days_back,
                    'financial_period': period
                },
                'crew_results': result,
                'summary': self._generate_research_summary(result),
                'recommendations': self._extract_recommendations(result),
                'risks': self._extract_risks(result),
                'opportunities': self._extract_opportunities(result)
            }
            
            self.logger.info(f"Successfully completed research for {ticker_symbol}")
            return research_report
            
        except Exception as e:
            self.logger.error(f"Error in stock research: {str(e)}")
            security_manager.log_security_event("research_error", {
                'error': str(e),
                'ticker': ticker_symbol
            })
            raise
    
    def research_multiple_stocks(self, ticker_symbols: List[str],
                               days_back: int = 7,
                               period: str = '1y') -> Dict[str, Any]:
        """
        Research multiple stocks for comparison.
        
        Args:
            ticker_symbols: List of stock ticker symbols
            days_back: Number of days of news to analyze
            period: Financial data period to analyze
            
        Returns:
            Dict containing comparative research results
        """
        results = {}
        
        for ticker in ticker_symbols:
            try:
                results[ticker] = self.research_stock(ticker, days_back, period)
            except Exception as e:
                self.logger.error(f"Error researching {ticker}: {str(e)}")
                results[ticker] = {'error': str(e)}
        
        return {
            'comparative_research': results,
            'research_date': datetime.now().isoformat(),
            'stocks_researched': len(ticker_symbols),
            'comparison_summary': self._generate_comparison_summary(results)
        }
    
    def _generate_research_summary(self, crew_results: Any) -> Dict[str, Any]:
        """Generate a summary of the research results."""
        # This would parse the crew results and create a summary
        return {
            'overall_assessment': 'neutral',
            'key_findings': [],
            'investment_thesis': '',
            'confidence_level': 'medium'
        }
    
    def _extract_recommendations(self, crew_results: Any) -> List[str]:
        """Extract investment recommendations from crew results."""
        # This would parse crew results for recommendations
        return ["Hold position", "Monitor closely", "Consider adding on dips"]
    
    def _extract_risks(self, crew_results: Any) -> List[str]:
        """Extract risk factors from crew results."""
        # This would parse crew results for risks
        return ["Market volatility", "Sector headwinds", "Regulatory changes"]
    
    def _extract_opportunities(self, crew_results: Any) -> List[str]:
        """Extract opportunities from crew results."""
        # This would parse crew results for opportunities
        return ["Market expansion", "Product innovation", "Cost optimization"]
    
    def _generate_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary comparing multiple stocks."""
        return {
            'best_performer': None,
            'worst_performer': None,
            'risk_comparison': {},
            'opportunity_comparison': {},
            'overall_ranking': []
        } 