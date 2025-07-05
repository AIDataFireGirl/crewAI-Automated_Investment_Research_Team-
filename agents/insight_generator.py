"""
Insight Generator Agent
Combines news analysis and financial reports to generate comprehensive investment insights.
"""

import os
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config.security import security_manager, rate_limit_decorator, input_validation_decorator

class InsightGeneratorAgent:
    """Agent responsible for generating comprehensive investment insights and recommendations."""
    
    def __init__(self):
        """Initialize the insight generator agent."""
        self.logger = logging.getLogger(__name__)
        
        # Define insight categories
        self.insight_categories = [
            'valuation', 'growth', 'risk', 'opportunity', 'technical',
            'fundamental', 'sentiment', 'market_timing', 'sector_analysis'
        ]
        
        # Risk assessment criteria
        self.risk_factors = [
            'volatility', 'beta', 'debt_levels', 'cash_flow', 'market_cap',
            'sector_risk', 'geographic_risk', 'regulatory_risk'
        ]
        
        # Investment recommendation levels
        self.recommendation_levels = [
            'strong_buy', 'buy', 'hold', 'sell', 'strong_sell'
        ]
    
    @rate_limit_decorator
    @input_validation_decorator
    def generate_comprehensive_insights(self, 
                                     news_data: Dict[str, Any],
                                     report_analysis: Dict[str, Any],
                                     market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive investment insights from news and report data.
        
        Args:
            news_data: News analysis results
            report_analysis: Financial report analysis results
            market_context: Additional market context data
            
        Returns:
            Dict containing comprehensive insights and recommendations
        """
        try:
            self.logger.info("Starting comprehensive insight generation")
            
            # Validate input data
            if not news_data or not report_analysis:
                raise ValueError("Both news_data and report_analysis are required")
            
            # Generate different types of insights
            valuation_insights = self._generate_valuation_insights(report_analysis)
            growth_insights = self._generate_growth_insights(report_analysis, news_data)
            risk_insights = self._generate_risk_insights(report_analysis, news_data)
            sentiment_insights = self._generate_sentiment_insights(news_data)
            technical_insights = self._generate_technical_insights(report_analysis)
            
            # Combine insights for final recommendation
            combined_insights = self._combine_insights(
                valuation_insights, growth_insights, risk_insights, 
                sentiment_insights, technical_insights
            )
            
            # Generate investment recommendation
            recommendation = self._generate_investment_recommendation(combined_insights)
            
            # Create comprehensive report
            comprehensive_insights = {
                'generated_at': datetime.now().isoformat(),
                'ticker_symbol': report_analysis.get('ticker_symbol', 'Unknown'),
                'valuation_insights': valuation_insights,
                'growth_insights': growth_insights,
                'risk_insights': risk_insights,
                'sentiment_insights': sentiment_insights,
                'technical_insights': technical_insights,
                'combined_insights': combined_insights,
                'investment_recommendation': recommendation,
                'confidence_score': self._calculate_confidence_score(combined_insights),
                'key_risks': self._identify_key_risks(risk_insights),
                'opportunities': self._identify_opportunities(growth_insights, sentiment_insights),
                'summary': self._generate_executive_summary(combined_insights, recommendation)
            }
            
            self.logger.info("Successfully generated comprehensive insights")
            return comprehensive_insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            security_manager.log_security_event("insight_generation_error", {
                'error': str(e)
            })
            raise
    
    def _generate_valuation_insights(self, report_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate valuation-related insights."""
        insights = {
            'valuation_metrics': {},
            'comparative_analysis': {},
            'fair_value_estimate': None,
            'valuation_conclusion': 'neutral'
        }
        
        try:
            company_info = report_analysis.get('company_info', {})
            
            # Analyze P/E ratio
            pe_ratio = company_info.get('pe_ratio', 0)
            forward_pe = company_info.get('forward_pe', 0)
            
            if pe_ratio > 0:
                insights['valuation_metrics']['pe_ratio'] = {
                    'value': pe_ratio,
                    'interpretation': self._interpret_pe_ratio(pe_ratio)
                }
            
            if forward_pe > 0:
                insights['valuation_metrics']['forward_pe'] = {
                    'value': forward_pe,
                    'interpretation': self._interpret_pe_ratio(forward_pe)
                }
            
            # Analyze price-to-book ratio
            pb_ratio = company_info.get('price_to_book', 0)
            if pb_ratio > 0:
                insights['valuation_metrics']['price_to_book'] = {
                    'value': pb_ratio,
                    'interpretation': self._interpret_pb_ratio(pb_ratio)
                }
            
            # Determine overall valuation conclusion
            insights['valuation_conclusion'] = self._determine_valuation_conclusion(
                insights['valuation_metrics']
            )
            
        except Exception as e:
            self.logger.warning(f"Error generating valuation insights: {str(e)}")
        
        return insights
    
    def _generate_growth_insights(self, report_analysis: Dict[str, Any], 
                                news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate growth-related insights."""
        insights = {
            'earnings_growth': {},
            'revenue_growth': {},
            'market_expansion': {},
            'growth_drivers': [],
            'growth_risks': []
        }
        
        try:
            # Analyze earnings growth
            earnings_analysis = report_analysis.get('earnings_analysis', {})
            avg_earnings_growth = earnings_analysis.get('avg_earnings_growth', 0)
            
            insights['earnings_growth'] = {
                'average_growth': avg_earnings_growth,
                'trend': 'increasing' if avg_earnings_growth > 0 else 'decreasing',
                'strength': self._assess_growth_strength(avg_earnings_growth)
            }
            
            # Analyze news sentiment for growth indicators
            news_articles = news_data.get('articles', [])
            growth_keywords = ['expansion', 'growth', 'increase', 'new market', 'acquisition']
            
            growth_mentions = 0
            for article in news_articles:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                
                for keyword in growth_keywords:
                    if keyword in title or keyword in description:
                        growth_mentions += 1
                        break
            
            insights['market_expansion'] = {
                'growth_mentions': growth_mentions,
                'sentiment': 'positive' if growth_mentions > len(news_articles) * 0.3 else 'neutral'
            }
            
        except Exception as e:
            self.logger.warning(f"Error generating growth insights: {str(e)}")
        
        return insights
    
    def _generate_risk_insights(self, report_analysis: Dict[str, Any], 
                              news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk-related insights."""
        insights = {
            'financial_risk': {},
            'market_risk': {},
            'operational_risk': {},
            'regulatory_risk': {},
            'overall_risk_level': 'medium'
        }
        
        try:
            company_info = report_analysis.get('company_info', {})
            financial_analysis = report_analysis.get('financial_analysis', {})
            
            # Analyze beta for market risk
            beta = company_info.get('beta', 1.0)
            insights['market_risk']['beta'] = {
                'value': beta,
                'interpretation': 'High volatility' if beta > 1.5 else 'Low volatility' if beta < 0.8 else 'Market average'
            }
            
            # Analyze liquidity risk
            liquidity_metrics = financial_analysis.get('liquidity_metrics', {})
            current_ratio = liquidity_metrics.get('current_ratio', 0)
            
            insights['financial_risk']['liquidity'] = {
                'current_ratio': current_ratio,
                'risk_level': 'high' if current_ratio < 1 else 'low' if current_ratio > 2 else 'medium'
            }
            
            # Analyze news for risk indicators
            risk_keywords = ['risk', 'concern', 'challenge', 'decline', 'loss', 'volatility']
            risk_mentions = 0
            
            news_articles = news_data.get('articles', [])
            for article in news_articles:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                
                for keyword in risk_keywords:
                    if keyword in title or keyword in description:
                        risk_mentions += 1
                        break
            
            insights['operational_risk']['news_risk_mentions'] = risk_mentions
            
            # Determine overall risk level
            insights['overall_risk_level'] = self._determine_overall_risk_level(insights)
            
        except Exception as e:
            self.logger.warning(f"Error generating risk insights: {str(e)}")
        
        return insights
    
    def _generate_sentiment_insights(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sentiment-related insights from news analysis."""
        insights = {
            'overall_sentiment': 'neutral',
            'sentiment_score': 0.0,
            'sentiment_trend': 'stable',
            'key_sentiment_drivers': [],
            'sentiment_breakdown': {}
        }
        
        try:
            articles = news_data.get('articles', [])
            if not articles:
                return insights
            
            # Calculate sentiment scores
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for article in articles:
                relevance_score = article.get('relevance_score', 0)
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                
                # Simple sentiment analysis based on keywords
                positive_words = ['growth', 'profit', 'increase', 'positive', 'strong']
                negative_words = ['decline', 'loss', 'negative', 'weak', 'concern']
                
                positive_matches = sum(1 for word in positive_words if word in title or word in description)
                negative_matches = sum(1 for word in negative_words if word in title or word in description)
                
                if positive_matches > negative_matches:
                    positive_count += relevance_score
                elif negative_matches > positive_matches:
                    negative_count += relevance_score
                else:
                    neutral_count += relevance_score
            
            # Calculate overall sentiment
            total_score = positive_count + negative_count + neutral_count
            if total_score > 0:
                sentiment_score = (positive_count - negative_count) / total_score
                insights['sentiment_score'] = sentiment_score
                
                if sentiment_score > 0.2:
                    insights['overall_sentiment'] = 'positive'
                elif sentiment_score < -0.2:
                    insights['overall_sentiment'] = 'negative'
                else:
                    insights['overall_sentiment'] = 'neutral'
            
        except Exception as e:
            self.logger.warning(f"Error generating sentiment insights: {str(e)}")
        
        return insights
    
    def _generate_technical_insights(self, report_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical analysis insights."""
        insights = {
            'price_trends': {},
            'support_resistance': {},
            'volume_analysis': {},
            'technical_indicators': {}
        }
        
        try:
            # This would typically involve technical analysis libraries
            # For now, we'll provide a basic structure
            insights['price_trends'] = {
                'current_trend': 'neutral',
                'trend_strength': 'medium',
                'price_momentum': 'stable'
            }
            
        except Exception as e:
            self.logger.warning(f"Error generating technical insights: {str(e)}")
        
        return insights
    
    def _combine_insights(self, valuation_insights: Dict[str, Any],
                         growth_insights: Dict[str, Any],
                         risk_insights: Dict[str, Any],
                         sentiment_insights: Dict[str, Any],
                         technical_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Combine all insights into a comprehensive view."""
        combined = {
            'valuation_score': self._calculate_valuation_score(valuation_insights),
            'growth_score': self._calculate_growth_score(growth_insights),
            'risk_score': self._calculate_risk_score(risk_insights),
            'sentiment_score': sentiment_insights.get('sentiment_score', 0),
            'technical_score': self._calculate_technical_score(technical_insights),
            'overall_score': 0.0,
            'strengths': [],
            'weaknesses': [],
            'neutral_factors': []
        }
        
        # Calculate overall score (weighted average)
        scores = [
            combined['valuation_score'] * 0.25,
            combined['growth_score'] * 0.25,
            combined['risk_score'] * 0.20,
            combined['sentiment_score'] * 0.20,
            combined['technical_score'] * 0.10
        ]
        
        combined['overall_score'] = sum(scores)
        
        # Identify strengths and weaknesses
        if combined['valuation_score'] > 0.6:
            combined['strengths'].append('Attractive valuation')
        elif combined['valuation_score'] < 0.4:
            combined['weaknesses'].append('Unattractive valuation')
        
        if combined['growth_score'] > 0.6:
            combined['strengths'].append('Strong growth prospects')
        elif combined['growth_score'] < 0.4:
            combined['weaknesses'].append('Weak growth prospects')
        
        if combined['risk_score'] < 0.4:
            combined['strengths'].append('Low risk profile')
        elif combined['risk_score'] > 0.6:
            combined['weaknesses'].append('High risk profile')
        
        return combined
    
    def _generate_investment_recommendation(self, combined_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment recommendation based on combined insights."""
        overall_score = combined_insights.get('overall_score', 0.5)
        
        # Determine recommendation level
        if overall_score >= 0.7:
            recommendation = 'buy'
            confidence = 'high'
        elif overall_score >= 0.6:
            recommendation = 'buy'
            confidence = 'medium'
        elif overall_score >= 0.4:
            recommendation = 'hold'
            confidence = 'medium'
        elif overall_score >= 0.3:
            recommendation = 'sell'
            confidence = 'medium'
        else:
            recommendation = 'sell'
            confidence = 'high'
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'score': overall_score,
            'rationale': self._generate_recommendation_rationale(combined_insights),
            'time_horizon': self._suggest_time_horizon(overall_score),
            'position_size': self._suggest_position_size(overall_score, combined_insights)
        }
    
    def _calculate_confidence_score(self, combined_insights: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        # This would be based on data quality, consistency, and coverage
        return 0.75  # Placeholder
    
    def _identify_key_risks(self, risk_insights: Dict[str, Any]) -> List[str]:
        """Identify key risks from risk analysis."""
        risks = []
        
        if risk_insights.get('overall_risk_level') == 'high':
            risks.append('High overall risk profile')
        
        market_risk = risk_insights.get('market_risk', {})
        if market_risk.get('beta', {}).get('value', 1.0) > 1.5:
            risks.append('High market volatility (beta > 1.5)')
        
        financial_risk = risk_insights.get('financial_risk', {})
        if financial_risk.get('liquidity', {}).get('risk_level') == 'high':
            risks.append('Liquidity concerns')
        
        return risks
    
    def _identify_opportunities(self, growth_insights: Dict[str, Any], 
                              sentiment_insights: Dict[str, Any]) -> List[str]:
        """Identify investment opportunities."""
        opportunities = []
        
        if growth_insights.get('earnings_growth', {}).get('strength') == 'strong':
            opportunities.append('Strong earnings growth trajectory')
        
        if sentiment_insights.get('overall_sentiment') == 'positive':
            opportunities.append('Positive market sentiment')
        
        return opportunities
    
    def _generate_executive_summary(self, combined_insights: Dict[str, Any], 
                                  recommendation: Dict[str, Any]) -> str:
        """Generate executive summary of the analysis."""
        score = combined_insights.get('overall_score', 0.5)
        rec = recommendation.get('recommendation', 'hold')
        
        summary = f"Overall Score: {score:.2f}/1.00\n"
        summary += f"Recommendation: {rec.upper()}\n"
        summary += f"Confidence: {recommendation.get('confidence', 'medium').title()}\n\n"
        
        strengths = combined_insights.get('strengths', [])
        weaknesses = combined_insights.get('weaknesses', [])
        
        if strengths:
            summary += "Key Strengths:\n"
            for strength in strengths:
                summary += f"• {strength}\n"
            summary += "\n"
        
        if weaknesses:
            summary += "Key Concerns:\n"
            for weakness in weaknesses:
                summary += f"• {weakness}\n"
        
        return summary
    
    # Helper methods for specific calculations
    def _interpret_pe_ratio(self, pe_ratio: float) -> str:
        """Interpret P/E ratio values."""
        if pe_ratio < 10:
            return 'Potentially undervalued'
        elif pe_ratio < 20:
            return 'Fairly valued'
        elif pe_ratio < 30:
            return 'Potentially overvalued'
        else:
            return 'Significantly overvalued'
    
    def _interpret_pb_ratio(self, pb_ratio: float) -> str:
        """Interpret price-to-book ratio values."""
        if pb_ratio < 1:
            return 'Potentially undervalued'
        elif pb_ratio < 3:
            return 'Fairly valued'
        else:
            return 'Potentially overvalued'
    
    def _assess_growth_strength(self, growth_rate: float) -> str:
        """Assess the strength of growth."""
        if growth_rate > 20:
            return 'strong'
        elif growth_rate > 10:
            return 'moderate'
        elif growth_rate > 0:
            return 'weak'
        else:
            return 'declining'
    
    def _determine_valuation_conclusion(self, valuation_metrics: Dict[str, Any]) -> str:
        """Determine overall valuation conclusion."""
        positive_count = 0
        negative_count = 0
        
        for metric in valuation_metrics.values():
            interpretation = metric.get('interpretation', '')
            if 'undervalued' in interpretation:
                positive_count += 1
            elif 'overvalued' in interpretation:
                negative_count += 1
        
        if positive_count > negative_count:
            return 'attractive'
        elif negative_count > positive_count:
            return 'unattractive'
        else:
            return 'neutral'
    
    def _determine_overall_risk_level(self, risk_insights: Dict[str, Any]) -> str:
        """Determine overall risk level."""
        risk_factors = []
        
        market_risk = risk_insights.get('market_risk', {})
        if market_risk.get('beta', {}).get('value', 1.0) > 1.5:
            risk_factors.append('high_volatility')
        
        financial_risk = risk_insights.get('financial_risk', {})
        if financial_risk.get('liquidity', {}).get('risk_level') == 'high':
            risk_factors.append('liquidity_risk')
        
        if len(risk_factors) >= 2:
            return 'high'
        elif len(risk_factors) == 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_valuation_score(self, valuation_insights: Dict[str, Any]) -> float:
        """Calculate valuation score (0-1)."""
        conclusion = valuation_insights.get('valuation_conclusion', 'neutral')
        
        if conclusion == 'attractive':
            return 0.8
        elif conclusion == 'unattractive':
            return 0.2
        else:
            return 0.5
    
    def _calculate_growth_score(self, growth_insights: Dict[str, Any]) -> float:
        """Calculate growth score (0-1)."""
        earnings_growth = growth_insights.get('earnings_growth', {})
        strength = earnings_growth.get('strength', 'weak')
        
        if strength == 'strong':
            return 0.8
        elif strength == 'moderate':
            return 0.6
        elif strength == 'weak':
            return 0.4
        else:
            return 0.2
    
    def _calculate_risk_score(self, risk_insights: Dict[str, Any]) -> float:
        """Calculate risk score (0-1, lower is better)."""
        risk_level = risk_insights.get('overall_risk_level', 'medium')
        
        if risk_level == 'low':
            return 0.2
        elif risk_level == 'medium':
            return 0.5
        else:
            return 0.8
    
    def _calculate_technical_score(self, technical_insights: Dict[str, Any]) -> float:
        """Calculate technical score (0-1)."""
        # Placeholder implementation
        return 0.5
    
    def _generate_recommendation_rationale(self, combined_insights: Dict[str, Any]) -> str:
        """Generate rationale for the recommendation."""
        strengths = combined_insights.get('strengths', [])
        weaknesses = combined_insights.get('weaknesses', [])
        
        rationale = "Based on comprehensive analysis: "
        
        if strengths:
            rationale += f"Strengths include {', '.join(strengths)}. "
        
        if weaknesses:
            rationale += f"Concerns include {', '.join(weaknesses)}. "
        
        return rationale
    
    def _suggest_time_horizon(self, overall_score: float) -> str:
        """Suggest investment time horizon."""
        if overall_score >= 0.7:
            return 'Long-term (2+ years)'
        elif overall_score >= 0.5:
            return 'Medium-term (6-18 months)'
        else:
            return 'Short-term (3-6 months)'
    
    def _suggest_position_size(self, overall_score: float, combined_insights: Dict[str, Any]) -> str:
        """Suggest position size based on score and risk."""
        risk_score = combined_insights.get('risk_score', 0.5)
        
        if overall_score >= 0.7 and risk_score < 0.4:
            return 'Large position (5-10% of portfolio)'
        elif overall_score >= 0.6:
            return 'Medium position (2-5% of portfolio)'
        elif overall_score >= 0.4:
            return 'Small position (1-2% of portfolio)'
        else:
            return 'Avoid or minimal position (<1% of portfolio)' 