"""
Created on 2025-01-17

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

    def test_lines_parsing(self):
        """
        Test parsing of lines input for routes
        """
        input_lines = """
        By bike:
        51.243931° N, 6.520022° E,
        51.269222° N, 6.625467° E:
        By train:
        51.269222° N, 6.625467° E,
        51.220189° N, 6.792675° E:
        By train:
        51.220189° N, 6.792675° E,
        49.600136° N, 6.134017° E:
        By train:
        49.600136° N, 6.134017° E,
        48.689858° N, 6.175906° E
        """

        # Expected parsed points
        expected_routes = [
            [(51.243931, 6.520022), (51.269222, 6.625467)],
            [(51.269222, 6.625467), (51.220189, 6.792675)],
            [(51.220189, 6.792675), (49.600136, 6.134017)],
            [(49.600136, 6.134017), (48.689858, 6.175906)]
        ]

        # Instantiate a viewer and parse lines
        viewer = GPXViewer()
        routes = viewer.parse_lines(input_lines)

        # Verify parsed routes match the expected
        self.assertEqual(len(routes), len(expected_routes))
        for route, expected in zip(routes, expected_routes):
            self.assertEqual(route, expected)
