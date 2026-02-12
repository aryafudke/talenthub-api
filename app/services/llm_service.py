from google import genai
import json
from typing import Optional, Dict, Any
from app.config import settings

# Configure Gemini Client
client = genai.Client(api_key=settings.gemini_api_key)


def parse_search_query(natural_query: str) -> Optional[Dict[str, Any]]:
    """
    Uses Gemini to parse natural language into search filters.
    
    Input: "senior engineers in Mumbai earning above 15 LPA"
    Output: {"designation": "senior engineer", "location": "Mumbai", "salary_min": 1500000}
    """
    
    prompt = f"""
You are a search query parser for an employee management system.

Convert the following natural language query into JSON search filters.
IGNORE any greetings, pleasantries, or casual conversation. Focus ONLY on employee search criteria.

Available filters:
- designation: Job title (string, use ILIKE matching)
- department_name: Department name (string)
- location: City/location (string)
- salary_min: Minimum salary in rupees (number)
- salary_max: Maximum salary in rupees (number)
- status: Employee status - "active", "inactive", or "on_leave"
- hire_date_after: Hired after this date (YYYY-MM-DD format)
- hire_date_before: Hired before this date (YYYY-MM-DD format)

IMPORTANT RULES:
1. Return ONLY valid JSON, no explanation, no markdown
2. Only include filters that are mentioned in the query
3. For salary in "LPA" (Lakhs Per Annum), multiply by 100000
   Example: 15 LPA = 1500000
4. IGNORE greetings like "hey", "hello", "how are you" - focus on search terms
5. If query has NO employee search criteria at all, return empty object {{}}

Examples:
- "hey, show me engineers" → {{"designation": "engineer"}}
- "hello, how are you" → {{}}
- "find software developers in Delhi" → {{"designation": "software developer", "location": "Delhi"}}

User Query: "{natural_query}"

JSON Output:
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        # Extract text from response
        response_text = response.text.strip()
        
        # Clean up response (remove markdown if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        filters = json.loads(response_text)
        return filters
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Response was: {response_text}")
        return None
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None