import requests
import json
from bs4 import BeautifulSoup

def web_search(query, num_results=3):
    url = "https://html.duckduckgo.com/html/"
    params = {
        'q': query,
        'kl': 'us-en'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.select('.result__body')[:num_results]:
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            url_elem = result.select_one('.result__url')
            
            if title_elem and snippet_elem:
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True)
                url = url_elem.get('href') if url_elem else ''
                
                results.append({
                    'title': title,
                    'snippet': snippet,
                    'url': url
                })
        
        print(f"Search query: {query}")
        print(f"Processed search results: {json.dumps(results, indent=2)}")
        return results
    except requests.RequestException as e:
        print(f"Error making request to DuckDuckGo: {e}")
    except Exception as e:
        print(f"Unexpected error during web search: {e}")
    
    return []

# Test the function independently
if __name__ == "__main__":
    test_query = "What are the main attractions in Central Park, New York?"
    results = web_search(test_query)
    print(f"Test query: {test_query}")
    print(f"Results: {json.dumps(results, indent=2)}")