"""
Test to verify trend data flow and LLM prompt generation
"""
import asyncio
import json
from app.services.assistant_service import AssistantService

async def test_trend_data_flow():
    """Test that trend queries fetch multi-year data and pass to LLM correctly"""
    
    service = AssistantService()
    
    # Test trend query
    query = "What trends do you see in Delhi?"
    
    print("=" * 80)
    print("Testing Trend Query Flow")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    try:
        # Process the query
        result = await service.query_assistant(query)
        
        print(f"Intent: {result.get('intent')}")
        print(f"Status: {result.get('status')}\n")
        
        # Check data structure
        data = result.get('data', {})
        print(f"Data Type: {data.get('type')}")
        print(f"Cities: {data.get('cities')}")
        print(f"Years: {data.get('years')}\n")
        
        # Show trend analysis
        trend_analysis = data.get('trend_analysis', {})
        if trend_analysis:
            print("TREND ANALYSIS DATA:")
            print(json.dumps(trend_analysis, indent=2))
        
        # Show LLM response
        print("\n" + "=" * 80)
        print("LLM RESPONSE:")
        print("=" * 80)
        answer = result.get('answer', '')
        print(answer)
        
        # Verify response contains data-driven content
        has_numbers = any(char.isdigit() for char in answer)
        has_city = "Delhi" in answer
        
        print("\n" + "=" * 80)
        print("VALIDATION:")
        print("=" * 80)
        print(f"✓ Has numerical values: {has_numbers}")
        print(f"✓ References city: {has_city}")
        print(f"✓ Not generic response: {'data unavailable' not in answer.lower()}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_multiple_cities_trend():
    """Test trend query with multiple cities"""
    
    service = AssistantService()
    query = "Show me trends in Delhi, Mumbai, and Bangalore"
    
    print("\n\n")
    print("=" * 80)
    print("Testing Multi-City Trend Query")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    try:
        result = await service.query_assistant(query)
        
        data = result.get('data', {})
        trend_analysis = data.get('trend_analysis', {})
        
        print(f"Cities with trend data: {list(trend_analysis.keys())}")
        print(f"Total years fetched: {len(data.get('years', []))}")
        
        if trend_analysis:
            for city, trends in trend_analysis.items():
                if trends:
                    first_val = trends[0].get('temperature')
                    last_val = trends[-1].get('temperature')
                    if first_val and last_val:
                        change = last_val - first_val
                        print(f"  {city}: {change:.1f}°C change over {len(trends)} periods")
        
        print("\n" + "=" * 80)
        print("LLM RESPONSE:")
        print("=" * 80)
        print(result.get('answer', ''))
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("TREND DATA FLOW TEST")
    print("=" * 80)
    print("This test verifies that trend queries:")
    print("1. Fetch multi-year historical data")
    print("2. Calculate year-over-year changes")
    print("3. Pass structured data to LLM")
    print("4. Generate data-driven responses\n")
    
    # Run tests
    asyncio.run(test_trend_data_flow())
    asyncio.run(test_multiple_cities_trend())
