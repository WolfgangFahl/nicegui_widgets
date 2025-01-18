"""
Created on 17.01.2025

@author: wf
"""

from ngwidgets.basetest import Basetest
from ngwidgets.gpxviewer import GPXViewer


class TestGPXViewer(Basetest):
    """
    test GPXViewer
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def test_gpx_viewer(self):
        """
        test the gpx viewer for all samples
        """
        sample_keys=list(GPXViewer.samples.keys())
        expected_centers = {
            sample_keys[0]: # Mountain bike loop at Middlesex Fells reservation.
                (42.44903, -71.1139805),
            sample_keys[1]: # Via Verde de Arditurri
                (43.302147, -1.8539505),
            sample_keys[2]: # Vía Verde del Fc Vasco Navarro
                (42.89977, -2.34528)
        }
        for sample_name, gpx_url in GPXViewer.samples.items():
            with self.subTest(sample_name=sample_name):
                viewer = GPXViewer.from_url(gpx_url)
                if self.debug:
                    print(f"{sample_name}:{viewer.gpx}")
                # Test GPX loaded successfully
                self.assertIsNotNone(viewer.gpx)
                # Test points were extracted
                self.assertGreater(len(viewer.points), 0)
                # Test map properties
                self.assertEqual(viewer.zoom, 11)
                exp_lat, exp_lon = expected_centers[sample_name]
                act_lat, act_lon = viewer.center
                self.assertAlmostEqual(act_lat, exp_lat, places=5)
                self.assertAlmostEqual(act_lon, exp_lon, places=5)

