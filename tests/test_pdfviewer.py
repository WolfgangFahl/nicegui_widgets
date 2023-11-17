'''
Created on 2023-09-18

@author: wf
'''
from ngwidgets.basetest import Basetest
from ngwidgets.pdfviewer import pdfjs_urls
from urllib import request

class TestPdfViewer(Basetest):
    """
    test PdfViewer
    """
    
    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
    
    def check_content_type(self,index,url: str, expected_type: str,timeout:float=3.2) -> bool:
        """
        check the content type
        """
        result=False
        debug=self.debug
        status_code=0
        checks={
            "css": ["{"],
            "js": ["function","/* Copyright"]
        }
        try:
            with request.urlopen(url, timeout=timeout) as response:
                status_code = response.getcode()
                if status_code == 200:
                    text = response.read().decode('utf-8')
                    for check in checks[expected_type]:
                        if check in text:
                            result=True
            symbol = "✔" if result else "❌"
        except Exception as _ex:
            symbol="⚠️"
        if debug:
            print(f"{index:3}:{expected_type:3}:{symbol}:{status_code}-{url}")
        return result
    
    def check_cdn(self,index,cdn,version,debug):
        """
        check the content delivery network
        """
        urls=pdfjs_urls(cdn,version,debug)
        urls.configure()
        self.assertTrue(self.check_content_type(index,urls.url["css"], "css"))
        self.assertTrue(self.check_content_type(index,urls.url["js_lib"], "js"))
        self.assertTrue(self.check_content_type(index,urls.url["js_viewer"], "js"))

    #@unittest.skipIf(Basetest.inPublicCI(), "unreliable in public CI")
    def test_cdns(self):
        """
        test content delivery networks
        """
        cdns=["github","jsdelivr"]
        if not super().inPublicCI():
            cdns.append("cdnjs")
            # cdns.append("unpkg")
        index=0
        for version in ["3.9.179","3.11.174"]:
            # unpkg is not tested due to unreliability see
            # https://github.com/mjackson/unpkg/issues/330
            for cdn in cdns:
                for debug in [False,True]:
                    with self.subTest(version=version, cdn=cdn, debug=debug):
                        index+=1
                        self.check_cdn(index,cdn, version, debug)