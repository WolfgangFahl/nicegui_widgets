"""
wikipedia.py
Conduct detailed searches against the Wikipedia API using the 'query' action
to fetch article titles, summaries, and direct URLs.

Created on 2024-06-22
@author: wf
"""

import requests


class WikipediaSearch:
    """
    A class for performing search queries against Wikipedia. This class leverages the MediaWiki API
    to obtain detailed article information including titles, summaries, and direct URLs.
    """

    def __init__(self, country="en"):
        """
        Initializes the WikipediaSearch class with the base URL for the Wikipedia API tailored to the specified language.

        Args:
            country (str): country code to configure the API URL, defaults to 'en' for English.
        """
        self.country = country
        self.base_url = f"https://{country}.wikipedia.org/w/api.php"
        self.session = (
            requests.Session()
        )  # Using a session for connection pooling to enhance performance.

    def search(self, query, limit=10, explain_text=False):
        """
        Performs a detailed search on Wikipedia by leveraging the 'query' action to fetch summaries,
        in addition to using the 'opensearch' API for quick search results.

        Args:
            query (str): The search string to query Wikipedia with.
            limit (int): The maximum number of search results to return. Default is 10.
            explain_text (bool): If True, return extracts as plain text. Default is True.

        Returns:
            list: A list of dictionaries, each containing the title, summary, and direct URL of an article.
        """

        # Setup parameters for the query action to fetch detailed information
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": 1,
            "prop": "info|extracts",  # Fetch page info and extracts
            "inprop": "url",  # Include the direct URL of each page
            "exintro": True,  # Only the introduction of each page
            "explaintext": explain_text,  # Return extracts as plain text
            "exlimit": "max",  # Maximum number of extracts
            "srlimit": limit,  # Limit the number of search results
        }
        response = self.session.get(self.base_url, params=params)
        search_results = response.json().get("query", {}).get("search", [])

        # Formulate results including summaries and URLs
        detailed_results = []
        for result in search_results:
            # Fetch page details with the correct use of parameters
            page_id = result["pageid"]
            page_params = {
                "action": "query",
                "prop": "info",
                "pageids": str(page_id),
                "inprop": "url",
                "format": "json",
            }
            page_response = self.session.get(self.base_url, params=page_params)
            page_info = page_response.json()["query"]["pages"][str(page_id)]
            url = page_info["fullurl"]  # Direct URL from the API

            detailed_result = {
                "title": result["title"],
                "summary": result.get("snippet", "No summary available."),
                "url": url,
            }
            detailed_results.append(detailed_result)

        return detailed_results
