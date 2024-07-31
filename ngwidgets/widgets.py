"""
Created on 2023-09-10

common nicegui widgets and tools

@author: wf


"""

import html
from urllib.parse import quote

from nicegui import ui


class Lang:
    """
    A class representing languages, providing utility methods related to language data.
    """

    @classmethod
    def get_language_dict(cls) -> dict:
        """
        Get a dictionary of supported languages.

        Returns:
            dict[str, str]: A dictionary where the keys are language codes (e.g., "en" for English)
                            and the values are the corresponding names/representations in HTML entity format.
        """
        # see https://github.com/sahajsk21/Anvesha/blob/master/src/components/topnav.js
        languages_list = [
            ["ar", "&#1575;&#1604;&#1593;&#1585;&#1576;&#1610;&#1577;"],
            ["arz", "&#1605;&#1589;&#1585;&#1609;"],
            ["ast", "Asturianu"],
            ["az", "Az&#601;rbaycanca"],
            ["azb", "&#1578;&#1734;&#1585;&#1705;&#1580;&#1607;"],
            [
                "be",
                "&#1041;&#1077;&#1083;&#1072;&#1088;&#1091;&#1089;&#1082;&#1072;&#1103;",
            ],
            ["bg", "&#1041;&#1098;&#1083;&#1075;&#1072;&#1088;&#1089;&#1082;&#1080;"],
            ["bn", "&#2476;&#2494;&#2434;&#2482;&#2494;"],
            ["ca", "Catal&agrave;"],
            ["ce", "&#1053;&#1086;&#1093;&#1095;&#1080;&#1081;&#1085;"],
            ["ceb", "Sinugboanong Binisaya"],
            ["cs", "&#268;e&scaron;tina"],
            ["cy", "Cymraeg"],
            ["da", "Dansk"],
            ["de", "Deutsch"],
            ["el", "&Epsilon;&lambda;&lambda;&eta;&nu;&iota;&kappa;&#940;"],
            ["en", "English"],
            ["eo", "Esperanto"],
            ["es", "Espa&ntilde;ol"],
            ["et", "Eesti"],
            ["eu", "Euskara"],
            ["fa", "&#1601;&#1575;&#1585;&#1587;&#1740;"],
            ["fi", "Suomi"],
            ["fr", "Fran&ccedil;ais"],
            ["gl", "Galego"],
            ["he", "&#1506;&#1489;&#1512;&#1497;&#1514;"],
            ["hi", "&#2361;&#2367;&#2344;&#2381;&#2342;&#2368;"],
            ["hr", "Hrvatski"],
            ["hu", "Magyar"],
            ["hy", "&#1344;&#1377;&#1397;&#1381;&#1408;&#1381;&#1398;"],
            ["id", "Bahasa Indonesia"],
            ["it", "Italiano"],
            ["ja", "&#26085;&#26412;&#35486;"],
            ["ka", "&#4325;&#4304;&#4320;&#4311;&#4323;&#4314;&#4312;"],
            [
                "kk",
                "&#1178;&#1072;&#1079;&#1072;&#1179;&#1096;&#1072; / Qazaq&#351;a / &#1602;&#1575;&#1586;&#1575;&#1602;&#1588;&#1575;",
            ],
            ["ko", "&#54620;&#44397;&#50612;"],
            ["la", "Latina"],
            ["lt", "Lietuvi&#371;"],
            ["lv", "Latvie&scaron;u"],
            ["min", "Bahaso Minangkabau"],
            ["ms", "Bahasa Melayu"],
            ["nan", "B&acirc;n-l&acirc;m-g&uacute; / H&#333;-l&oacute;-o&#275;"],
            ["nb", "Norsk (bokm&aring;l)"],
            ["nl", "Nederlands"],
            ["nn", "Norsk (nynorsk)"],
            ["pl", "Polski"],
            ["pt", "Portugu&ecirc;s"],
            ["ro", "Rom&acirc;n&#259;"],
            ["ru", "&#1056;&#1091;&#1089;&#1089;&#1082;&#1080;&#1081;"],
            [
                "sh",
                "Srpskohrvatski / &#1057;&#1088;&#1087;&#1089;&#1082;&#1086;&#1093;&#1088;&#1074;&#1072;&#1090;&#1089;&#1082;&#1080;",
            ],
            ["sk", "Sloven&#269;ina"],
            ["sl", "Sloven&scaron;&#269;ina"],
            ["sr", "&#1057;&#1088;&#1087;&#1089;&#1082;&#1080; / Srpski"],
            ["sv", "Svenska"],
            ["ta", "&#2980;&#2990;&#3007;&#2996;&#3021;"],
            ["tg", "&#1058;&#1086;&#1207;&#1080;&#1082;&#1251;"],
            ["th", "&#3616;&#3634;&#3625;&#3634;&#3652;&#3607;&#3618;"],
            ["tr", "T&uuml;rk&ccedil;e"],
            [
                "tt",
                "&#1058;&#1072;&#1090;&#1072;&#1088;&#1095;&#1072; / Tatar&ccedil;a",
            ],
            [
                "uk",
                "&#1059;&#1082;&#1088;&#1072;&#1111;&#1085;&#1089;&#1100;&#1082;&#1072;",
            ],
            ["ur", "&#1575;&#1585;&#1583;&#1608;"],
            [
                "uz",
                "O&#699;zbekcha / &#1038;&#1079;&#1073;&#1077;&#1082;&#1095;&#1072;",
            ],
            ["vi", "Ti&#7871;ng Vi&#7879;t"],
            ["vo", "Volap&uuml;k"],
            ["war", "Winaray"],
            ["yue", "&#31925;&#35486;"],
            ["zh", "&#20013;&#25991;"],
        ]
        languages_dict = {}
        for code, desc in languages_list:
            desc = html.unescape(desc)
            languages_dict[code] = desc

        return languages_dict


class Link:
    """
    a link
    """

    red = "color: red;text-decoration: underline;"
    blue = "color: blue;text-decoration: underline;"

    @staticmethod
    def create(
        url, text, tooltip=None, target=None, style: str = None, url_encode=False
    ):
        """
        Create a link for the given URL and text, with optional URL encoding.

        Args:
            url (str): The URL.
            text (str): The link text.
            tooltip (str): An optional tooltip.
            target (str): Target attribute, e.g., _blank for opening the link in a new tab.
            style (str): CSS style to be applied.
            url_encode (bool): Flag to indicate if the URL needs encoding. default: False

        Returns:
            str: HTML anchor tag as a string.
        """
        if url_encode:
            url = quote(url)

        title = "" if tooltip is None else f" title='{tooltip}'"
        target = "" if target is None else f" target='{target}'"
        if style is None:
            style = Link.blue
        style = f" style='{style}'"
        link = f"<a href='{url}'{title}{target}{style}>{text}</a>"
        return link


class About(ui.element):
    """
    About Div for a given version
    """

    def __init__(
        self,
        version,
        font_size=24,
        font_family="Helvetica, Arial, sans-serif",
        **kwargs,
    ):
        """
        construct an about Div for the given version
        """

        def add(html, l, code):
            html += f'<div class="about_row"><div class="about_column1">{l}:</div><div class="about_column2">{code}</div></div>'
            return html

        super().__init__(tag="div", **kwargs)
        with self:
            doc_link = Link.create(
                url=version.doc_url, text="documentation", target="_blank"
            )
            disc_link = Link.create(
                url=version.chat_url, text="discussion", target="_blank"
            )
            cm_link = Link.create(url=version.cm_url, text="source", target="_blank")
            max_label_length = 7  # e.g. updated
            column1_width = (
                font_size * max_label_length
            )  # Approximate width calculation

            html = f"""<style>
                    .about_row {{
                        display: flex;
                        align-items: baseline;
                    }}
                    .about_column1 {{
                        font-weight: bold;
                        font-size: {font_size}px;
                        text-align: right;
                        width: {column1_width}px; 
                        padding-right: 10px;
                        font-family: {font_family};
                    }}
                    .about_column2 {{
                        font-size: {font_size}px;
                        font-family: {font_family};
                    }}
                    .about_column2 a {{
                        color: blue;
                        text-decoration: underline;
                    }}
               </style>"""
            html = add(html, "name", f"{version.name}")
            html = add(html, "purpose", f"{version.description}")
            html = add(html, "version", f"{version.version}")
            html = add(html, "since", f"{version.date}")
            html = add(html, "updated", f"{version.updated}")
            html = add(html, "authors", f"{version.authors}")
            html = add(html, "docs", doc_link)
            html = add(html, "chat", disc_link)
            html = add(html, "source", cm_link)
            ui.html(html)


class HideShow:
    """
    A class representing a hideable/showable section in a NiceGUI application.
    """

    TRIANGLE_LEFT = "◀"
    TRIANGLE_DOWN = "▼"

    def __init__(
        self,
        hide_show_label: tuple[str, str] = None,
        show_content: bool = True,
        content_div=None,
        lazy_init: bool = False,
        **kwargs,
    ):
        """
        Initialize the HideShow component.

        Args:
            hide_show_label: Labels for shown/hidden states.
            show_content: Initial visibility state (default True).
            content_div: Div with content to hide/show.
            lazy_init: If True, content_div initialized later.
            **kwargs: Additional args for button element.
        """
        self.label_if_shown, self.label_if_hidden = hide_show_label
        self.show_content = show_content
        self.btn = ui.button(
            text=self._get_status_label(show_content),
            on_click=self.toggle_hide_show,
            **kwargs,
        )

        if not lazy_init:
            self.content_div = content_div if content_div else ui.element()
        else:
            self.content_div = None

        self._set_show_content(show_content)

    def _set_show_content(self, show_content: bool):
        """
        Set visibility of content.
        """
        if self.content_div:
            self.show_content = show_content
            self.content_div.set_visibility(show_content)
            self.btn.set_text(self._get_status_label(show_content))

    def _get_status_label(self, show_content: bool) -> str:
        """
        Get label text based on visibility state.
        """
        icon = self.TRIANGLE_DOWN if show_content else self.TRIANGLE_LEFT
        label = (
            self.label_if_shown
            if show_content
            else (self.label_if_hidden if self.label_if_hidden else self.label_if_shown)
        )
        return f"{label} {icon}"

    def toggle_hide_show(self, _=None):
        """
        Toggle visibility of content.
        """
        self._set_show_content(not self.show_content)

    def add(self, widget):
        """
        Add a widget to content div.
        """
        self.content_div.add(widget)

    def update(self):
        """
        Update the content div.
        """
        self.content_div.update()

    def set_content(self, content_div=None):
        """
        Set or update content div.
        """
        self.content_div = content_div if content_div else ui.element()
        self._set_show_content(self.show_content)
