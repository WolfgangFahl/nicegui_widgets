"""
Created on 2024-06-22

@author: wf
"""

import json

from ngwidgets.basetest import Basetest
from ngwidgets.wikipedia import WikipediaSearch


class TestWikipediaSearch(Basetest):
    """
    test Wikipedia Search
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.wikipedia_search = WikipediaSearch()

    def test_wikipedia_search(self):
        """
        Test the Wikipedia search function by querying a known term and checking the response.
        This test verifies that the search for 'Software engineering' returns relevant entries.
        """
        query = "Software engineering"
        expected_title = (
            "Software engineering"  # Corrected to expected title relevant to the query
        )
        results = self.wikipedia_search.search(query)

        # Debug print if needed
        if self.debug:
            print(f"Search results for '{query}': \n{json.dumps(results, indent=2)}")

        # Check if the expected title is in the results
        found = any(expected_title in result["title"] for result in results)
        self.assertTrue(
            found, f"Expected to find '{expected_title}' in the search results."
        )
