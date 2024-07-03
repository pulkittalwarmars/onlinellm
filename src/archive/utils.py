import requests
from bs4 import BeautifulSoup
import re

def web_search(query, num_results=5):
    url = "https://html.duckduckgo.com/html/"
    params = {'q': query, 'kl': 'us-en'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.select('.result__body'):
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            url_elem = result.select_one('.result__url')
            
            if title_elem and snippet_elem and not re.search(r'Ad$', title_elem.text):
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True)
                url = url_elem.get('href') if url_elem else ''
                
                results.append({
                    'title': title,
                    'snippet': snippet,
                    'url': url
                })
            
            if len(results) >= num_results:
                break
        
        print(f"Search query: {query}")
        print(f"Processed search results: {results}")
        return results
    except Exception as e:
        print(f"Error in web search: {e}")
        return []