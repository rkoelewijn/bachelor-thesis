import requests

class OWIClient:
    """
    A client to interface with the Open Web Search Remote Index.
    """
    def __init__(self, api_endpoint="https://api.openwebsearch.eu/v1/search"):
        self.api_endpoint = api_endpoint

    def search_artist_at_venue(self, artist_name, venue_domain="doornroosje.nl"):
        """
        Queries the OWI for a specific artist on a specific venue's domain.
        Returns the raw text of the most relevant page found.
        """
        # Construct the query: site restricted search for the artist name
        query = f"site:{venue_domain} \"{artist_name}\""
        
        params = {
            'q': query,
            'format': 'json',
            'size': 1 # We only need the top result for fact-checking
        }

        try:
            response = requests.get(self.api_endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get('results'):
                # Extract the main text content from the OWI crawl
                return data['results'][0].get('content', '')
            
            return ""
        except Exception as e:
            print(f"⚠️ OWI Query Failed for {artist_name}: {e}")
            return ""