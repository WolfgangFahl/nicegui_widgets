"""
Created on 2023-12-03

@author: wf
"""

from ngwidgets.basetest import Basetest
from ngwidgets.dateparser import DateParser

class TestDateParser(Basetest):
    """
    test date parser
    """
    
    def test_dateparser(self):
        """
        test the dateparser
        """
        date_parser=DateParser()
        test_cases = [
            ("Thu Jun 02 11:56:53 CDT 2011", "2011-06-02T16:56:53Z"), # Adjusted for UTC
            ("Wed, 16 Nov 2022 06:00:01 +0100", "2022-11-16T05:00:01Z"), # Adjusted for UTC
            ("Tue, 01 Jun 2004 11:09:50 +0200", "2004-06-01T09:09:50Z"), # Adjusted for UTC
             # Add more test cases here
        ]

        for date_input, expected_output in test_cases:
            result = date_parser.parse_date(date_input)
            self.assertEqual(result, expected_output, f"Failed for {date_input}")
        