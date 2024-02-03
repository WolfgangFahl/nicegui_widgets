"""
Created on 2023-12-03

@author: wf
"""

import json

from ngwidgets.basetest import Basetest
from ngwidgets.dateparser import DateParser


class TestDateParser(Basetest):
    """
    test date parser
    """

    def test_aliases(self):
        """
        test the aliases
        """
        date_parser = DateParser()
        debug = self.debug
        if debug:
            for org, repl in date_parser.aliases:
                print(f"{org}->{repl}")

    def test_dateparser(self):
        """
        test the dateparser
        """
        date_parser = DateParser()
        test_cases = [
            ("Tue, 17 Apr 2001 19:26:26 Eastern Daylight Time", "2001-04-17T23:26:26Z"),
            ('Wed, 16 Mar 2005 14:46:37 "GMT"', "2005-03-16T14:46:37Z"),
            ("Tue, 7 Jan 1997 00:19:06 +-800", "1997-01-07T08:19:06Z"),
            ("19 Feb 01 16:34:12 +-0100", "2001-02-19T17:34:12Z"),
            (
                "Wed, 31 Jul 2002 11:27:35 +0100 (GMT Daylight Time)",
                "2002-07-31T10:27:35Z",
            ),
            ("Mon, 2 Sep 1996 09:34:44 +0100 (WET DST)", "1996-09-02T08:34:44Z"),
            ("Wed, 8 Oct 1997 07:12:42 +0200 (METDST)", "1997-10-08T05:12:42Z"),
            (
                "Sun, 23 Aug 1998 15:04:33 -0600 (Mountain Daylight Time)",
                "1998-08-23T21:04:33Z",
            ),
            ("Thu, 15 May 97 22:33:07 pst", "1997-05-16T06:33:07Z"),
            (
                "Sun, 18 Dec 2011 14:25:36 +0100 (added by postmaster@deutschebahn.com)",
                "2011-12-18T13:25:36Z",
            ),
            ("Wed, 20 May 98 13:44 MET DST", "1998-05-20T11:44:00Z"),
            ("Wed, 9 Dec 1998 14:35:54 +0200 (IST)", "1998-12-09T09:05:54Z"),
            ("Mon, 29 Mar 1999 16:12:30 -0330 (NST)", "1999-03-29T12:42:30Z"),
            ("Wed, 17 May 2006 14:26:33 +0100 (Etc/GMT)", "2006-05-17T15:26:33Z"),
            ("Fri May 1 11:50:05 2009 METDST", "2009-05-01T09:50:05Z"),
            ("Wed, 25 Feb 2009 07:15:38 +0100 (GMT+01:00)", "2009-02-25T06:15:38Z"),
            ("Fri, 21 Sep 2001 20:51:53 +0200 (MET DST)", "2001-09-21T18:51:53Z"),
            (
                "Thu Jun 02 11:56:53 CDT 2011",
                "2011-06-02T16:56:53Z",
            ),  # Adjusted for UTC
            (
                "Wed, 16 Nov 2022 06:00:01 +0100",
                "2022-11-16T05:00:01Z",
            ),  # Adjusted for UTC
            (
                "Tue, 01 Jun 2004 11:09:50 +0200",
                "2004-06-01T09:09:50Z",
            ),  # Adjusted for UTC
            # Add more test cases here
        ]

        for date_input, expected_output in test_cases:
            result = date_parser.parse_date(date_input)
            self.assertEqual(result, expected_output, f"Failed for {date_input}")
