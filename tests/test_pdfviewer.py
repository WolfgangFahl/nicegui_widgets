'''
Created on 2023-09-18

@author: wf
'''
from tests.basetest import Basetest
from ngwidgets.pdfviewer import pdfjs_urls
import requests

class TestPdfViewer(Basetest):
    """
    test PdfViewer
    """
    
    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
    
    def check_content_type(self,url: str, expected_type: str,timeout:float=1.6) -> bool:
        result=False
        debug=self.debug
        status_code=0
        checks={
            "css": ["{"],
            "js": ["function","/* Copyright"]
        }
        try:
            response = requests.get(url,timeout=timeout)
            status_code=response.status_code
            if response.status_code == 200:
                text=response.text
                for check in checks[expected_type]:
                    if check in text:
                        result=True
            symbol = "✔" if result else "❌"
        except Exception as _ex:
            symbol="⚠️"
        if debug:
            print(f"{status_code}:{expected_type}:{symbol}:{url}")
        return result
    
    def check_cdn(self,cdn,version,debug):
        """
        check the content delivery network
        """
        urls=pdfjs_urls(cdn,version,debug)
        urls.configure()
        self.assertTrue(self.check_content_type(urls.url["css"], "css"))
        self.assertTrue(self.check_content_type(urls.url["js_lib"], "js"))
        self.assertTrue(self.check_content_type(urls.url["js_viewer"], "js"))

    def test_cdns(self):
        """
        test content delivery networks
        """
        for version in ["3.9.179","3.10.111"]:
            # unpkg is not tested due to unreliability see
            # https://github.com/mjackson/unpkg/issues/330
            for cdn in ["github","jsdelivr","cdnjs"]:
                for debug in [False,True]:
                    with self.subTest(version=version, cdn=cdn, debug=debug):
                        self.check_cdn(cdn, version, debug)