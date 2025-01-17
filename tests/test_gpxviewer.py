'''
Created on 17.01.2025

@author: wf
'''
from ngwidgets.basetest import Basetest
from ngwidgets.gpx import GPXViewer

class TestGPXViewer(Basetest):
    """
    test GPXViewer
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def test_gpx_viewer(self):
        """
        test the gpx viewer
        """
        gpx_url="https://www.bahntrassenradwege.de/images/Spanien/Baskenland/V-v-de-arditurri/Arditurri2.gpx"
        viewer=GPXViewer.from_url(gpx_url)
        if self.debug:
            print(viewer.gpx)


