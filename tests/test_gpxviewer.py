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
        Test the GPX viewer functionality for all sample GPX files.
        Tests loading GPX files, tour creation, and center calculation.
        """
        sample_keys = list(GPXViewer.samples.keys())
        expected_centers = {
            sample_keys[0]: (  # Mountain bike loop at Middlesex Fells reservation.
                42.44903,
                -71.1139805,
            ),
            sample_keys[1]: (43.302147, -1.8539505),  # Via Verde de Arditurri
            sample_keys[2]: (42.89977, -2.34528),  # Vía Verde del Fc Vasco Navarro
        }

        for sample_name, gpx_url in GPXViewer.samples.items():
            with self.subTest(sample_name=sample_name):
                # Create viewer instance and load GPX file
                viewer = GPXViewer.from_url(gpx_url)

                viewer.set_center()

                if self.debug:
                    print(f"{sample_name}:{viewer.gpx}")
                    viewer.tour.dump()

                # Test GPX loaded successfully
                self.assertIsNotNone(viewer.gpx)

                # Test that tour and legs were created
                self.assertIsNotNone(viewer.tour)
                self.assertGreater(
                    len(viewer.tour.legs), 0, f"No legs found in {sample_name}"
                )

                # Test map properties
                self.assertEqual(viewer.zoom, GPXViewer.default_zoom)

                # Test center calculation
                exp_lat, exp_lon = expected_centers[sample_name]
                act_lat, act_lon = viewer.center

                self.assertAlmostEqual(
                    act_lat,
                    exp_lat,
                    places=5,
                    msg=f"Latitude mismatch for {sample_name}",
                )
                self.assertAlmostEqual(
                    act_lon,
                    exp_lon,
                    places=5,
                    msg=f"Longitude mismatch for {sample_name}",
                )

                # Test bounding box calculation
                self.assertIsNotNone(
                    viewer.bounding_box,
                    f"Bounding box not calculated for {sample_name}",
                )

                # Test map creation with leg styles
                viewer.show()
                self.assertIsNotNone(viewer.map, f"Map not created for {sample_name}")

    def test_lines_parsing(self):
        """
        Test parsing of lines input for routes.
        """
        input_lines = """
        By bike→
        51.243931° N, 6.520022° E,
        51.269222° N, 6.625467° E:
        By train→
        51.269222° N, 6.625467° E,
        51.220189° N, 6.792675° E:
        By train→
        51.220189° N, 6.792675° E,
        49.600136° N, 6.134017° E:
        By train→
        49.600136° N, 6.134017° E,
        48.689858° N, 6.175906° E
        """

        # Expected parsed legs
        expected_legs = [
            ("bike", (51.243931, 6.520022), (51.269222, 6.625467)),
            ("train", (51.269222, 6.625467), (51.220189, 6.792675)),
            ("train", (51.220189, 6.792675), (49.600136, 6.134017)),
            ("train", (49.600136, 6.134017), (48.689858, 6.175906)),
        ]

        # Instantiate the GPXViewer and parse lines
        viewer = GPXViewer()
        tour = viewer.parse_lines(input_lines)
        viewer.set_center()
        if self.debug:
            viewer.tour.dump()

        # Verify tour name
        self.assertEqual(tour.name, "Parsed Tour")

        # Verify number of legs
        self.assertEqual(len(tour.legs), len(expected_legs))

        # Verify parsed legs
        for leg, (expected_type, expected_start, expected_end) in zip(
            tour.legs, expected_legs
        ):
            self.assertEqual(leg.leg_type, expected_type)
            self.assertEqual(leg.start.coordinates, expected_start)
            self.assertEqual(leg.end.coordinates, expected_end)
