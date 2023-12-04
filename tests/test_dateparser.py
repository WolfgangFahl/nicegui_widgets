"""
Created on 2023-12-03

@author: wf
"""

from ngwidgets.basetest import Basetest
from ngwidgets.dateparser import DateParser
import json

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
            ("Wed, 17 May 2006 14:26:33 +0100 (Etc/GMT)","2006-05-17T15:26:33Z"),
            ("Fri May 1 11:50:05 2009 METDST","2009-05-01T09:50:05Z"),
            ("Wed, 25 Feb 2009 07:15:38 +0100 (GMT+01:00)","2009-02-25T06:15:38Z"),
            ("Fri, 21 Sep 2001 20:51:53 +0200 (MET DST)","2001-09-21T18:51:53Z"),
            ("Thu Jun 02 11:56:53 CDT 2011", "2011-06-02T16:56:53Z"), # Adjusted for UTC
            ("Wed, 16 Nov 2022 06:00:01 +0100", "2022-11-16T05:00:01Z"), # Adjusted for UTC
            ("Tue, 01 Jun 2004 11:09:50 +0200", "2004-06-01T09:09:50Z"), # Adjusted for UTC
             # Add more test cases here
        ]

        for date_input, expected_output in test_cases:
            result = date_parser.parse_date(date_input)
            self.assertEqual(result, expected_output, f"Failed for {date_input}")
        