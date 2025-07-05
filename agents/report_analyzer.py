"""
Report Analyzer Agent
Analyzes financial reports, earnings calls, and regulatory filings to extract key insights.
"""

import os
import logging
import json
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config.security import security_manager, rate_limit_decorator, input_validation_decorator

class ReportAnalyzerAgent:
    """Agent responsible for analyzing financial reports and extracting insights."""
    
    def __init__(self):
        """Initialize the report analyzer agent."""
        self.logger = logging.getLogger(__name__)
        
        # Define report types to analyze
        self.report_types = [
            'earnings', 'quarterly', 'annual', '10-k', '10-q', 
            '8-k', 'proxy', 'prospectus'
        ]
        
        # Key financial metrics to extract
        self.key_metrics = [
            'revenue', 'net_income', 'earnings_per_share', 'cash_flow',
            'debt', 'assets', 'liabilities', 'equity', 'margins',
            'growth_rate', 'return_on_equity', 'return_on_assets'
        ]
        
        # Sentiment keywords for analysis
        self.positive_keywords = [
            'growth', 'increase', 'improve', 'strong', 'positive',
            'profit', 'gain', 'upside', 'opportunity', 'expansion'
        ]
        
        self.negative_keywords = [
            'decline', 'decrease', 'loss', 'weak', 'negative',
            'risk', 'concern', 'challenge', 'downturn', 'reduction'
        ]
    
    @rate_limit_decorator
    @input_validation_decorator
    def analyze_company_reports(self, ticker_symbol: str, 
                              report_type: str = 'all',
                              period: str = '1y') -> Dict[str, Any]:
        """
        Analyze financial reports for a specific company.
        
        Args:
            ticker_symbol: Stock ticker symbol
            report_type: Type of report to analyze ('all', 'earnings', 'quarterly', etc.)
            period: Time period to analyze ('1m', '3m', '6m', '1y', '2y')
            
        Returns:
            Dict containing analysis results and insights
        """
        try:
            self.logger.info(f"Starting report analysis for {ticker_symbol}")
            
            # Validate ticker symbol
            if not security_manager.validate_ticker_symbol(ticker_symbol):
                raise ValueError(f"Invalid ticker symbol: {ticker_symbol}")
            
            # Get company information
            company_info = self._get_company_info(ticker_symbol)
            
            # Get financial data
            financial_data = self._get_financial_data(ticker_symbol, period)
            
            # Analyze earnings reports
            earnings_analysis = self._analyze_earnings_reports(ticker_symbol, period)
            
            # Analyze balance sheet and income statement
            financial_analysis = self._analyze_financial_statements(financial_data)
            
            # Generate insights
            insights = self._generate_insights(
                company_info, financial_data, earnings_analysis, financial_analysis
            )
            
            analysis_result = {
                'ticker_symbol': ticker_symbol,
                'analysis_date': datetime.now().isoformat(),
                'period_analyzed': period,
                'company_info': company_info,
                'financial_data': financial_data,
                'earnings_analysis': earnings_analysis,
                'financial_analysis': financial_analysis,
                'insights': insights,
                'summary': self._generate_analysis_summary(insights)
            }
            
            self.logger.info(f"Successfully analyzed reports for {ticker_symbol}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing reports for {ticker_symbol}: {str(e)}")
            security_manager.log_security_event("report_analysis_error", {
                'error': str(e),
                'ticker': ticker_symbol
            })
            raise
    
    def _get_company_info(self, ticker_symbol: str) -> Dict[str, Any]:
        """Get basic company information."""
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', 'Unknown'),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0)
            }
        except Exception as e:
            self.logger.warning(f"Error getting company info for {ticker_symbol}: {str(e)}")
            return {}
    
    def _get_financial_data(self, ticker_symbol: str, period: str) -> Dict[str, Any]:
        """Get financial data for analysis."""
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Get financial statements
            balance_sheet = ticker.balance_sheet
            income_stmt = ticker.income_stmt
            cash_flow = ticker.cashflow
            
            # Get historical price data
            hist = ticker.history(period=period)
            
            return {
                'balance_sheet': balance_sheet.to_dict() if balance_sheet is not None else {},
                'income_statement': income_stmt.to_dict() if income_stmt is not None else {},
                'cash_flow': cash_flow.to_dict() if cash_flow is not None else {},
                'price_history': hist.to_dict() if hist is not None else {},
                'period': period
            }
        except Exception as e:
            self.logger.warning(f"Error getting financial data for {ticker_symbol}: {str(e)}")
            return {}
    
    def _analyze_earnings_reports(self, ticker_symbol: str, period: str) -> Dict[str, Any]:
        """Analyze earnings reports and call transcripts."""
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Get earnings dates
            earnings_dates = ticker.earnings_dates
            
            analysis = {
                'earnings_dates': earnings_dates.to_dict() if earnings_dates is not None else {},
                'earnings_growth': [],
                'revenue_growth': [],
                'eps_trends': [],
                'surprises': []
            }
            
            # Analyze earnings trends
            if earnings_dates is not None and not earnings_dates.empty:
                # Calculate earnings growth
                eps_values = earnings_dates['Earnings'].dropna()
                if len(eps_values) > 1:
                    growth_rates = []
                    for i in range(1, len(eps_values)):
                        if eps_values.iloc[i-1] != 0:
                            growth = ((eps_values.iloc[i] - eps_values.iloc[i-1]) / 
                                    abs(eps_values.iloc[i-1])) * 100
                            growth_rates.append(growth)
                    
                    analysis['earnings_growth'] = growth_rates
                    analysis['avg_earnings_growth'] = sum(growth_rates) / len(growth_rates) if growth_rates else 0
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"Error analyzing earnings for {ticker_symbol}: {str(e)}")
            return {}
    
    def _analyze_financial_statements(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze balance sheet, income statement, and cash flow."""
        analysis = {
            'profitability_metrics': {},
            'liquidity_metrics': {},
            'efficiency_metrics': {},
            'growth_metrics': {},
            'risk_metrics': {}
        }
        
        try:
            balance_sheet = financial_data.get('balance_sheet', {})
            income_stmt = financial_data.get('income_statement', {})
            cash_flow = financial_data.get('cash_flow', {})
            
            # Calculate key ratios if data is available
            if balance_sheet and income_stmt:
                # Get most recent data
                latest_balance = list(balance_sheet.values())[0] if balance_sheet else {}
                latest_income = list(income_stmt.values())[0] if income_stmt else {}
                
                # Profitability metrics
                if 'Total Revenue' in latest_income and 'Net Income' in latest_income:
                    revenue = latest_income['Total Revenue']
                    net_income = latest_income['Net Income']
                    if revenue and revenue != 0:
                        analysis['profitability_metrics']['net_margin'] = (net_income / revenue) * 100
                
                # Liquidity metrics
                if 'Total Current Assets' in latest_balance and 'Total Current Liabilities' in latest_balance:
                    current_assets = latest_balance['Total Current Assets']
                    current_liabilities = latest_balance['Total Current Liabilities']
                    if current_liabilities and current_liabilities != 0:
                        analysis['liquidity_metrics']['current_ratio'] = current_assets / current_liabilities
                
                # Efficiency metrics
                if 'Total Assets' in latest_balance and 'Total Revenue' in latest_income:
                    total_assets = latest_balance['Total Assets']
                    revenue = latest_income['Total Revenue']
                    if total_assets and total_assets != 0:
                        analysis['efficiency_metrics']['asset_turnover'] = revenue / total_assets
            
        except Exception as e:
            self.logger.warning(f"Error analyzing financial statements: {str(e)}")
        
        return analysis
    
    def _generate_insights(self, company_info: Dict[str, Any], 
                          financial_data: Dict[str, Any],
                          earnings_analysis: Dict[str, Any],
                          financial_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from all analyzed data."""
        insights = []
        
        try:
            # Valuation insights
            if company_info.get('pe_ratio'):
                pe_ratio = company_info['pe_ratio']
                if pe_ratio > 25:
                    insights.append({
                        'type': 'valuation',
                        'category': 'high_pe',
                        'message': f'High P/E ratio of {pe_ratio:.2f} suggests premium valuation',
                        'severity': 'warning'
                    })
                elif pe_ratio < 10:
                    insights.append({
                        'type': 'valuation',
                        'category': 'low_pe',
                        'message': f'Low P/E ratio of {pe_ratio:.2f} suggests potential undervaluation',
                        'severity': 'positive'
                    })
            
            # Earnings growth insights
            avg_growth = earnings_analysis.get('avg_earnings_growth', 0)
            if avg_growth > 20:
                insights.append({
                    'type': 'earnings',
                    'category': 'strong_growth',
                    'message': f'Strong earnings growth of {avg_growth:.1f}%',
                    'severity': 'positive'
                })
            elif avg_growth < -10:
                insights.append({
                    'type': 'earnings',
                    'category': 'declining_earnings',
                    'message': f'Declining earnings growth of {avg_growth:.1f}%',
                    'severity': 'negative'
                })
            
            # Financial health insights
            current_ratio = financial_analysis.get('liquidity_metrics', {}).get('current_ratio', 0)
            if current_ratio < 1:
                insights.append({
                    'type': 'financial_health',
                    'category': 'liquidity_concern',
                    'message': f'Low current ratio of {current_ratio:.2f} indicates potential liquidity issues',
                    'severity': 'warning'
                })
            elif current_ratio > 2:
                insights.append({
                    'type': 'financial_health',
                    'category': 'strong_liquidity',
                    'message': f'Strong current ratio of {current_ratio:.2f} indicates good liquidity',
                    'severity': 'positive'
                })
            
            # Sector comparison insights
            sector = company_info.get('sector', '')
            if sector and sector != 'Unknown':
                insights.append({
                    'type': 'sector',
                    'category': 'sector_info',
                    'message': f'Company operates in {sector} sector',
                    'severity': 'info'
                })
            
        except Exception as e:
            self.logger.warning(f"Error generating insights: {str(e)}")
        
        return insights
    
    def _generate_analysis_summary(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of the analysis."""
        if not insights:
            return {
                'overall_sentiment': 'neutral',
                'key_findings': [],
                'recommendations': []
            }
        
        # Count insights by severity
        severity_counts = {}
        for insight in insights:
            severity = insight.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Determine overall sentiment
        positive_count = severity_counts.get('positive', 0)
        negative_count = severity_counts.get('negative', 0)
        warning_count = severity_counts.get('warning', 0)
        
        if positive_count > (negative_count + warning_count):
            overall_sentiment = 'positive'
        elif negative_count > (positive_count + warning_count):
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Generate recommendations
        recommendations = []
        if severity_counts.get('negative', 0) > 2:
            recommendations.append('Consider reducing position or waiting for improvement')
        if severity_counts.get('positive', 0) > 2:
            recommendations.append('Consider increasing position or adding to portfolio')
        if severity_counts.get('warning', 0) > 1:
            recommendations.append('Monitor closely for potential issues')
        
        return {
            'overall_sentiment': overall_sentiment,
            'insight_count': len(insights),
            'severity_breakdown': severity_counts,
            'key_findings': [insight['message'] for insight in insights[:5]],
            'recommendations': recommendations
        }
    
    def analyze_multiple_companies(self, ticker_symbols: List[str], 
                                 period: str = '1y') -> Dict[str, Any]:
        """
        Analyze multiple companies for comparison.
        
        Args:
            ticker_symbols: List of stock ticker symbols
            period: Time period to analyze
            
        Returns:
            Dict containing comparative analysis
        """
        results = {}
        
        for ticker in ticker_symbols:
            try:
                results[ticker] = self.analyze_company_reports(ticker, period=period)
            except Exception as e:
                self.logger.error(f"Error analyzing {ticker}: {str(e)}")
                results[ticker] = {'error': str(e)}
        
        return {
            'comparative_analysis': results,
            'analysis_date': datetime.now().isoformat(),
            'companies_analyzed': len(ticker_symbols)
        } 