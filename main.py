#!/usr/bin/env python3
"""
Main Execution Script for Automated Investment Research Team
Demonstrates how to use the CrewAI investment research system.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crew.investment_research_crew import InvestmentResearchCrew
from config.security import security_manager

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('investment_research.log'),
            logging.StreamHandler()
        ]
    )

def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    return True

def research_single_stock(ticker_symbol: str) -> Dict[str, Any]:
    """
    Research a single stock using the investment research crew.
    
    Args:
        ticker_symbol: Stock ticker symbol to research
        
    Returns:
        Dict containing research results
    """
    try:
        print(f"\n🔍 Starting comprehensive research for {ticker_symbol}...")
        
        # Initialize the research crew
        crew = InvestmentResearchCrew()
        
        # Perform research
        results = crew.research_stock(ticker_symbol)
        
        print(f"✅ Research completed for {ticker_symbol}")
        return results
        
    except Exception as e:
        print(f"❌ Error researching {ticker_symbol}: {str(e)}")
        return {'error': str(e)}

def research_multiple_stocks(ticker_symbols: List[str]) -> Dict[str, Any]:
    """
    Research multiple stocks for comparison.
    
    Args:
        ticker_symbols: List of stock ticker symbols
        
    Returns:
        Dict containing comparative research results
    """
    try:
        print(f"\n🔍 Starting comparative research for {len(ticker_symbols)} stocks...")
        
        # Initialize the research crew
        crew = InvestmentResearchCrew()
        
        # Perform research
        results = crew.research_multiple_stocks(ticker_symbols)
        
        print(f"✅ Comparative research completed")
        return results
        
    except Exception as e:
        print(f"❌ Error in comparative research: {str(e)}")
        return {'error': str(e)}

def save_results(results: Dict[str, Any], filename: str = None):
    """
    Save research results to a JSON file.
    
    Args:
        results: Research results to save
        filename: Optional filename, defaults to timestamp-based name
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_results_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")

def display_summary(results: Dict[str, Any]):
    """
    Display a summary of research results.
    
    Args:
        results: Research results to summarize
    """
    print("\n" + "="*60)
    print("📊 RESEARCH SUMMARY")
    print("="*60)
    
    if 'error' in results:
        print(f"❌ Research failed: {results['error']}")
        return
    
    ticker = results.get('ticker_symbol', 'Unknown')
    research_date = results.get('research_date', 'Unknown')
    
    print(f"Stock: {ticker}")
    print(f"Research Date: {research_date}")
    
    # Display recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print(f"\n📈 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Display risks
    risks = results.get('risks', [])
    if risks:
        print(f"\n⚠️  Key Risks:")
        for i, risk in enumerate(risks, 1):
            print(f"  {i}. {risk}")
    
    # Display opportunities
    opportunities = results.get('opportunities', [])
    if opportunities:
        print(f"\n🎯 Opportunities:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp}")
    
    print("\n" + "="*60)

def main():
    """Main execution function."""
    print("🚀 Automated Investment Research Team")
    print("="*50)
    
    # Setup logging
    setup_logging()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Validate security configuration
    if not security_manager.validate_api_key(os.getenv('OPENAI_API_KEY'), 'openai'):
        print("❌ Invalid OpenAI API key")
        sys.exit(1)
    
    print("✅ Environment validated successfully")
    
    # Example usage
    print("\n📋 Example Usage:")
    print("1. Research a single stock")
    print("2. Research multiple stocks for comparison")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                ticker = input("Enter stock ticker symbol (e.g., AAPL): ").strip().upper()
                if ticker:
                    results = research_single_stock(ticker)
                    display_summary(results)
                    save_results(results)
                else:
                    print("❌ Please enter a valid ticker symbol")
            
            elif choice == '2':
                tickers_input = input("Enter stock ticker symbols separated by commas (e.g., AAPL,MSFT,GOOGL): ").strip()
                if tickers_input:
                    tickers = [t.strip().upper() for t in tickers_input.split(',')]
                    results = research_multiple_stocks(tickers)
                    save_results(results)
                    print(f"✅ Comparative research completed for {len(tickers)} stocks")
                else:
                    print("❌ Please enter valid ticker symbols")
            
            elif choice == '3':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        
        except KeyboardInterrupt:
            print("\n👋 Research interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

def demo_mode():
    """Run in demo mode with predefined examples."""
    print("🎯 Running in Demo Mode")
    print("="*30)
    
    # Example stocks for demo
    demo_stocks = ['AAPL', 'MSFT', 'GOOGL']
    
    print(f"Researching demo stocks: {', '.join(demo_stocks)}")
    
    for stock in demo_stocks:
        print(f"\n🔍 Researching {stock}...")
        results = research_single_stock(stock)
        display_summary(results)
        
        # Save individual results
        save_results(results, f"demo_{stock}_research.json")
    
    # Comparative analysis
    print(f"\n📊 Running comparative analysis...")
    comparative_results = research_multiple_stocks(demo_stocks)
    save_results(comparative_results, "demo_comparative_analysis.json")
    
    print("\n✅ Demo completed successfully!")

if __name__ == "__main__":
    # Check if running in demo mode
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo_mode()
    else:
        main() 