"""
Created on 2023-12-03

@author: wf
"""

import re

import pytz
from dateutil import parser


class DateParser:
    """A parser for converting date strings with timezone information into ISO 8601 format.

    Attributes:
        aliases (list): A list of tuples mapping timezone string aliases to their canonical form.
        whois_timezone_info (dict): A dictionary mapping timezone abbreviations to their UTC offsets.
    """

    def __init__(self):
        # https://stackoverflow.com/a/54629675/1497139
        self.aliases = [
            ('"GMT"', "(GMT)"),
            ("(WET DST)", "(WEST)"),
            ("+0200 (MET DST)", "+0200"),
            ("+0200 (METDST)", "+0200"),
            (" METDST", " +0200"),
            (" MET DST", " +0200"),
            ("(GMT)", "+0000"),
            ("+0100 (GMT Daylight Time)", "+0100"),
            ("+0100 (Etc/GMT)", "-0100"),
            ("Etc/GMT", "-0000"),
            (" pst", " PST"),  # Convert lowercase 'pst' to uppercase 'PST'
            (" est", " EST"),
            ("(MSK/MSD)", "(MSK)"),
            ("(GMT Standard Time)", "(GMT)"),
            ("(Mountain Daylight Time)", "(MDT)"),
            (" Eastern Daylight Time", "-0800 (EDT)"),
            ("(Eastern Standard Time)", "(EST)"),
            ("(Eastern Daylight Time)", "(EDT)"),
            ("(Pacific Daylight Time)", "(PDT)"),
            ("(Eastern Standard Time)", "(EST)"),
        ]
        self.regexp_aliases = [
            # remove superfluous (added by ...)
            (r"\(added by [^\)]+\)", ""),
            # Regular expression to remove conflicting timezone information like (GMT-1)
            # but only if it follows a standard timezone offset like +0100
            # example +0100 (GMT-1)
            (r"(\+\d{4}|\-\d{4}) \(GMT[+-]\d+\)", r"\1"),
            # Regular expression to correct conflicting timezone information like +-0100
            # +-0100
            (r"\+\-(\d{4})", r"-\1"),  # Convert +-0100 to -0100
            # Regular expression to correct timezone information like +-800
            (r"\+\-(\d{3})", r"-0\1"),  # Convert +-800 to -0800
        ]
        # Add generic aliases for a range of timezones
        for hour in range(-12, 15):  # Ranges from GMT-12 to GMT+14
            sign = "+" if hour >= 0 else "-"
            hour_abs = abs(hour)

            # Example: ("(GMT+00:00)","+0000")
            self.aliases.append(
                (f"(GMT{sign}{hour_abs:02d}:00)", f"{sign}{hour_abs:02d}00")
            )
            # Example: ("(GMT-1)","-0100"),
            self.aliases.append((f"(GMT{sign}{hour})", f"{sign}0{hour_abs}00"))

            # Handling Etc/GMT formats
            # Example: ("Etc/GMT+1", "+0100")
            gmt_sign = "" if hour <= 0 else "+"
            self.aliases.append((f"Etc/GMT{gmt_sign}{hour}", f"{sign}{hour_abs:02d}00"))

        self.timezone_hours = {
            "AoE": {"offset": -12, "description": "Anywhere on Earth"},
            "Y": {"offset": -12, "description": "Yankee Time Zone"},
            "NUT": {"offset": -11, "description": "Niue Time"},
            "SST": {"offset": -11, "description": "Samoa Standard Time"},
            "X": {"offset": -11, "description": "X-ray Time Zone"},
            "CKT": {"offset": -10, "description": "Cook Island Time"},
            "HST": {"offset": -10, "description": "Hawaii Standard Time"},
            "TAHT": {"offset": -10, "description": "Tahiti Time"},
            "W": {"offset": -10, "description": "Whiskey Time Zone"},
            "AKST": {"offset": -9, "description": "Alaska Standard Time"},
            "GAMT": {"offset": -9, "description": "Gambier Time"},
            "HDT": {"offset": -9, "description": "Hawaii-Aleutian Daylight Time"},
            "V": {"offset": -9, "description": "Victor Time Zone"},
            "AKDT": {"offset": -8, "description": "Alaska Daylight Time"},
            "PST": {"offset": -8, "description": "Pacific Standard Time"},
            "PT": {"offset": -8, "description": "Pacific Time"},
            "U": {"offset": -8, "description": "Uniform Time Zone"},
            "MST": {"offset": -7, "description": "Mountain Standard Time"},
            "MT": {"offset": -7, "description": "Mountain Time"},
            "PDT": {"offset": -7, "description": "Pacific Daylight Time"},
            "T": {"offset": -7, "description": "Tango Time Zone"},
            "CST": {"offset": -6, "description": "Central Standard Time"},
            "CT": {"offset": -6, "description": "Central Time"},
            "EAST": {"offset": -6, "description": "Easter Island Standard Time"},
            "GALT": {"offset": -6, "description": "Galapagos Time"},
            "MDT": {"offset": -6, "description": "Mountain Daylight Time"},
            "S": {"offset": -6, "description": "Sierra Time Zone"},
            "ACT": {"offset": -5, "description": "Acre Time"},
            "CDT": {"offset": -5, "description": "Central Daylight Time"},
            "CIST": {"offset": -5, "description": "Clipperton Island Standard Time"},
            "COT": {"offset": -5, "description": "Colombia Time"},
            "EASST": {"offset": -5, "description": "Easter Island Summer Time"},
            "ECT": {"offset": -5, "description": "Ecuador Time"},
            "EST": {"offset": -5, "description": "Eastern Standard Time"},
            "ET": {"offset": -5, "description": "Eastern Time"},
            "PET": {"offset": -5, "description": "Peru Time"},
            "R": {"offset": -5, "description": "Romeo Time Zone"},
            "AMT": {"offset": -4, "description": "Amazon Time"},
            "AT": {"offset": -4, "description": "Atlantic Time"},
            "BOT": {"offset": -4, "description": "Bolivia Time"},
            "CIDST": {"offset": -4, "description": "Cambridge Bay Daylight Time"},
            "CLT": {"offset": -4, "description": "Chile Standard Time"},
            "EDT": {"offset": -4, "description": "Eastern Daylight Time"},
            "FKT": {"offset": -4, "description": "Falkland Islands Time"},
            "GYT": {"offset": -4, "description": "Guyana Time"},
            "PYT": {"offset": -4, "description": "Paraguay Time"},
            "Q": {"offset": -4, "description": "Quebec Time Zone"},
            "VET": {"offset": -4, "description": "Venezuelan Standard Time"},
            "AMST": {"offset": -3, "description": "Amazon Summer Time"},
            "ART": {"offset": -3, "description": "Argentina Time"},
            "BRT": {"offset": -3, "description": "Brasilia Time"},
            "CLST": {"offset": -3, "description": "Chile Summer Time"},
            "FKST": {"offset": -3, "description": "Falkland Islands Summer Time"},
            "GFT": {"offset": -3, "description": "French Guiana Time"},
            "P": {"offset": -3, "description": "Papa Time Zone"},
            "PMST": {"offset": -3, "description": "Pierre & Miquelon Standard Time"},
            "PYST": {"offset": -3, "description": "Paraguay Summer Time"},
            "ROTT": {"offset": -3, "description": "Rothera Time"},
            "SRT": {"offset": -3, "description": "Suriname Time"},
            "UYT": {"offset": -3, "description": "Uruguay Time"},
            "WARST": {"offset": -3, "description": "Western Argentina Summer Time"},
            "WGT": {"offset": -3, "description": "West Greenland Time"},
            "BRST": {"offset": -2, "description": "Brasilia Summer Time"},
            "FNT": {"offset": -2, "description": "Fernando de Noronha Time"},
            "O": {"offset": -2, "description": "Oscar Time Zone"},
            "PMDT": {"offset": -2, "description": "Pierre & Miquelon Daylight Time"},
            "UYST": {"offset": -2, "description": "Uruguay Summer Time"},
            "WGST": {"offset": -2, "description": "West Greenland Summer Time"},
            "AZOT": {"offset": -1, "description": "Azores Standard Time"},
            "CVT": {"offset": -1, "description": "Cape Verde Time"},
            "EGT": {"offset": -1, "description": "Eastern Greenland Time"},
            "N": {"offset": -1, "description": "November Time Zone"},
            "AZOST": {"offset": 0, "description": "Azores Summer Time"},
            "EGST": {"offset": 0, "description": "Eastern Greenland Summer Time"},
            "GMT": {"offset": 0, "description": "Greenwich Mean Time"},
            "UT": {"offset": 0, "description": "Universal Time"},
            "UTC": {"offset": 0, "description": "Coordinated Universal Time"},
            "WET": {"offset": 0, "description": "Western European Time"},
            "WT": {"offset": 0, "description": "Western Sahara Standard Time"},
            "Z": {"offset": 0, "description": "Zulu Time Zone"},
            "A": {"offset": 1, "description": "Alpha Time Zone"},
            "CET": {"offset": 1, "description": "Central European Time"},
            "MET": {"offset": 1, "description": "Middle European Time"},
            "MEZ": {"offset": 1, "description": "Middle European Time"},
            "WAT": {"offset": 1, "description": "West Africa Time"},
            "WEST": {"offset": 1, "description": "Western European Summer Time"},
            "B": {"offset": 2, "description": "Bravo Time Zone"},
            "CAT": {"offset": 2, "description": "Central Africa Time"},
            "CEDT": {"offset": 2, "description": "Central European Daylight Time"},
            "CES": {"offset": 2, "description": "Central European Summer Time"},
            "CEST": {"offset": 2, "description": "Central European Summer Time"},
            "EET": {"offset": 2, "description": "Eastern European Time"},
            "MES": {"offset": 2, "description": "Middle European Summer Time"},
            "MEST": {"offset": 2, "description": "Middle European Summer Time"},
            "MESZ": {"offset": 2, "description": "Middle European Summer Time"},
            "METDST": {
                "offset": 2,
                "description": "Middle European Time Daylight Saving Time",
            },
            "MET DST": {
                "offset": 2,
                "description": "Middle European Time Daylight Saving Time",
            },
            "SAST": {"offset": 2, "description": "South Africa Standard Time"},
            "WAST": {"offset": 2, "description": "West Africa Summer Time"},
            "NDT": {"offset": 2.5, "description": "Newfoundland Daylight Time"},
            "AST": {"offset": 3, "description": "Arabia Standard Time"},
            "C": {"offset": 3, "description": "Charlie Time Zone"},
            "EAT": {"offset": 3, "description": "East Africa Time"},
            "EEST": {"offset": 3, "description": "Eastern European Summer Time"},
            "FET": {"offset": 3, "description": "Further-Eastern European Time"},
            "IDT": {"offset": 3, "description": "Israel Daylight Time"},
            "MSK": {"offset": 3, "description": "Moscow Time"},
            "SYOT": {"offset": 3, "description": "Syowa Time"},
            "TRT": {"offset": 3, "description": "Turkey Time"},
            "IRST": {"offset": 3.5, "description": "Iran Standard Time"},
            "NST": {"offset": 3.5, "description": "Newfoundland Standard Time"},
            "ADT": {"offset": 4, "description": "Atlantic Daylight Time"},
            "AZT": {"offset": 4, "description": "Azerbaijan Time"},
            "D": {"offset": 4, "description": "Delta Time Zone"},
            "GET": {"offset": 4, "description": "Georgia Standard Time"},
            "GST": {"offset": 4, "description": "Gulf Standard Time"},
            "KUYT": {"offset": 4, "description": "Kuybyshev Time"},
            "MSD": {"offset": 4, "description": "Moscow Daylight Time"},
            "MUT": {"offset": 4, "description": "Mauritius Time"},
            "RET": {"offset": 4, "description": "Réunion Time"},
            "SAMT": {"offset": 4, "description": "Samara Time"},
            "SCT": {"offset": 4, "description": "Seychelles Time"},
            "AFT": {"offset": 4.5, "description": "Afghanistan Time"},
            "IRDT": {"offset": 4.5, "description": "Iran Daylight Time"},
            "AQTT": {"offset": 5, "description": "Aqtobe Time"},
            "AZST": {"offset": 5, "description": "Azerbaijan Summer Time"},
            "E": {"offset": 5, "description": "Echo Time Zone"},
            "MAWT": {"offset": 5, "description": "Mawson Station Time"},
            "MVT": {"offset": 5, "description": "Maldives Time"},
            "ORAT": {"offset": 5, "description": "Oral Time"},
            "PKT": {"offset": 5, "description": "Pakistan Standard Time"},
            "TFT": {"offset": 5, "description": "French Southern and Antarctic Time"},
            "TJT": {"offset": 5, "description": "Tajikistan Time"},
            "TMT": {"offset": 5, "description": "Turkmenistan Time"},
            "UZT": {"offset": 5, "description": "Uzbekistan Time"},
            "YEKT": {"offset": 5, "description": "Yekaterinburg Time"},
            "IST": {"offset": 5.5, "description": "Indian Standard Time"},
            "NPT": {"offset": 5.5, "description": "Nepal Time"},
            "ALMT": {"offset": 6, "description": "Alma-Ata Time"},
            "BST": {"offset": 6, "description": "Bangladesh Standard Time"},
            "BTT": {"offset": 6, "description": "Bhutan Time"},
            "F": {"offset": 6, "description": "Foxtrot Time Zone"},
            "IOT": {"offset": 6, "description": "Indian Ocean Time"},
            "KGT": {"offset": 6, "description": "Kyrgyzstan Time"},
            "OMST": {"offset": 6, "description": "Omsk Time"},
            "QYZT": {"offset": 6, "description": "Qyzylorda Time"},
            "VOST": {"offset": 6, "description": "Vostok Station Time"},
            "YEKST": {"offset": 6, "description": "Yekaterinburg Summer Time"},
            "CCT": {"offset": 6.5, "description": "Cocos Islands Time"},
            "MMT": {"offset": 6.5, "description": "Myanmar Time"},
            "CXT": {"offset": 7, "description": "Christmas Island Time"},
            "DAVT": {"offset": 7, "description": "Davis Time"},
            "G": {"offset": 7, "description": "Golf Time Zone"},
            "HOVT": {"offset": 7, "description": "Hovd Time"},
            "ICT": {"offset": 7, "description": "Indochina Time"},
            "KRAT": {"offset": 7, "description": "Krasnoyarsk Time"},
            "NOVST": {"offset": 7, "description": "Novosibirsk Summer Time"},
            "NOVT": {"offset": 7, "description": "Novosibirsk Time"},
            "OMSST": {"offset": 7, "description": "Omsk Summer Time"},
            "WIB": {"offset": 7, "description": "Western Indonesia Time"},
            "AWST": {"offset": 8, "description": "Australian Western Standard Time"},
            "BNT": {"offset": 8, "description": "Brunei Time"},
            "CAST": {"offset": 8, "description": "Casey Time"},
            "CHOT": {"offset": 8, "description": "Choibalsan Time"},
            "H": {"offset": 8, "description": "Hotel Time Zone"},
            "HKT": {"offset": 8, "description": "Hong Kong Time"},
            "HOVST": {"offset": 8, "description": "Hovd Summer Time"},
            "IRKT": {"offset": 8, "description": "Irkutsk Time"},
            "KRAST": {"offset": 8, "description": "Krasnoyarsk Summer Time"},
            "MYT": {"offset": 8, "description": "Malaysia Time"},
            "PHT": {"offset": 8, "description": "Philippine Time"},
            "SGT": {"offset": 8, "description": "Singapore Time"},
            "ULAT": {"offset": 8, "description": "Ulaanbaatar Time"},
            "WITA": {"offset": 8, "description": "Central Indonesia Time"},
            "ACWST": {
                "offset": 8.75,
                "description": "Australian Central Western Standard Time",
            },
            "AWDT": {"offset": 9, "description": "Australian Western Daylight Time"},
            "CHOST": {"offset": 9, "description": "Choibalsan Summer Time"},
            "I": {"offset": 9, "description": "India Time Zone"},
            "IRKST": {"offset": 9, "description": "Irkutsk Summer Time"},
            "JST": {"offset": 9, "description": "Japan Standard Time"},
            "KST": {"offset": 9, "description": "Korea Standard Time"},
            "PWT": {"offset": 9, "description": "Palau Time"},
            "TLT": {"offset": 9, "description": "Timor Leste Time"},
            "ULAST": {"offset": 9, "description": "Ulaanbaatar Summer Time"},
            "WIT": {"offset": 9, "description": "Eastern Indonesia Time"},
            "YAKT": {"offset": 9, "description": "Yakutsk Time"},
            "ACST": {"offset": 9.5, "description": "Australian Central Standard Time"},
            "MART": {"offset": 9.5, "description": "Marquesas Time"},
            "AEST": {"offset": 10, "description": "Australian Eastern Standard Time"},
            "AET": {"offset": 10, "description": "Australian Eastern Time"},
            "CHUT": {"offset": 10, "description": "Chuuk Time"},
            "ChST": {"offset": 10, "description": "Chamorro Standard Time"},
            "DDUT": {"offset": 10, "description": "Dumont d'Urville Time"},
            "K": {"offset": 10, "description": "Kilo Time Zone"},
            "PGT": {"offset": 10, "description": "Papua New Guinea Time"},
            "VLAT": {"offset": 10, "description": "Vladivostok Time"},
            "YAKST": {"offset": 10, "description": "Yakutsk Summer Time"},
            "YAPT": {"offset": 10, "description": "Yap Time"},
            # Continuing from the previous part...
            "ACDT": {"offset": 10.5, "description": "Australian Central Daylight Time"},
            "LHST": {"offset": 10.5, "description": "Lord Howe Standard Time"},
            "AEDT": {"offset": 11, "description": "Australian Eastern Daylight Time"},
            "KOST": {"offset": 11, "description": "Kosrae Time"},
            "L": {"offset": 11, "description": "Lima Time Zone"},
            "LHDT": {"offset": 11, "description": "Lord Howe Daylight Time"},
            "MAGT": {"offset": 11, "description": "Magadan Time"},
            "NCT": {"offset": 11, "description": "New Caledonia Time"},
            "NFT": {"offset": 11, "description": "Norfolk Time"},
            "PONT": {"offset": 11, "description": "Pohnpei Time"},
            "SAKT": {"offset": 11, "description": "Sakhalin Time"},
            "SBT": {"offset": 11, "description": "Solomon Islands Time"},
            "SRET": {"offset": 11, "description": "Srednekolymsk Time"},
            "VLAST": {"offset": 11, "description": "Vladivostok Summer Time"},
            "VUT": {"offset": 11, "description": "Vanuatu Time"},
            "ANAST": {"offset": 12, "description": "Anadyr Summer Time"},
            "ANAT": {"offset": 12, "description": "Anadyr Time"},
            "FJT": {"offset": 12, "description": "Fiji Time"},
            "GILT": {"offset": 12, "description": "Gilbert Island Time"},
            "M": {"offset": 12, "description": "Mike Time Zone"},
            "MAGST": {"offset": 12, "description": "Magadan Summer Time"},
            "MHT": {"offset": 12, "description": "Marshall Islands Time"},
            "NRT": {"offset": 12, "description": "Nauru Time"},
            "NZST": {"offset": 12, "description": "New Zealand Standard Time"},
            "PETST": {"offset": 12, "description": "Kamchatka Summer Time"},
            "PETT": {"offset": 12, "description": "Kamchatka Time"},
            "TVT": {"offset": 12, "description": "Tuvalu Time"},
            "WAKT": {"offset": 12, "description": "Wake Island Time"},
            "WFT": {"offset": 12, "description": "Wallis and Futuna Time"},
            "CHAST": {"offset": 12.75, "description": "Chatham Standard Time"},
            "FJST": {"offset": 13, "description": "Fiji Summer Time"},
            "NZDT": {"offset": 13, "description": "New Zealand Daylight Time"},
            "PHOT": {"offset": 13, "description": "Phoenix Island Time"},
            "TKT": {"offset": 13, "description": "Tokelau Time"},
            "TOT": {"offset": 13, "description": "Tonga Time"},
            "CHADT": {"offset": 13.75, "description": "Chatham Daylight Time"},
            "LINT": {"offset": 14, "description": "Line Islands Time"},
            "TOST": {"offset": 14, "description": "Tonga Summer Time"},
            "WST": {"offset": 14, "description": "West Samoa Time"},
        }
        # Convert timezone offsets from hours to seconds and create tzinfos dictionary
        self.tzinfos = {}
        for tz, info in self.timezone_hours.items():
            offset_in_seconds = int(info["offset"] * 3600)
            self.tzinfos[tz] = offset_in_seconds

    def parse_date(self, date_str) -> str:
        """
        Parses a date string and converts it to ISO 8601 format.

        Args:
            date_str (str): The date string to be parsed.

        Returns:
            str:  the ISO 8601 date string
        """
        # Apply regex replacements
        for pattern, replacement in self.regexp_aliases:
            date_str = re.sub(pattern, replacement, date_str)

        # Apply simple string replacements
        for alias, replacement in self.aliases:
            date_str = date_str.replace(alias, replacement)

        parsed_date = parser.parse(date_str, tzinfos=self.tzinfos)
        parsed_date_z = parsed_date.astimezone(pytz.utc)
        # Convert to ISO 8601 format
        iso_date_str = parsed_date_z.isoformat()
        iso_date_str_z = iso_date_str.replace("+00:00", "Z")
        return iso_date_str_z
