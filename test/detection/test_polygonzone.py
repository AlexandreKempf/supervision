from contextlib import ExitStack as DoesNotRaise
from test.test_utils import mock_detections

import numpy as np
import pytest

import supervision as sv

DETECTION_BOXES = np.array(
    [
        [35.0, 35.0, 65.0, 65.0],
        [60.0, 60.0, 90.0, 90.0],
        [85.0, 85.0, 115.0, 115.0],
        [110.0, 110.0, 140.0, 140.0],
        [135.0, 135.0, 165.0, 165.0],
        [160.0, 160.0, 190.0, 190.0],
        [185.0, 185.0, 215.0, 215.0],
        [210.0, 210.0, 240.0, 240.0],
        [235.0, 235.0, 265.0, 265.0],
    ],
    dtype=np.float32,
)

DETECTIONS = mock_detections(
    xyxy=DETECTION_BOXES, class_id=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
)

POLYGON = np.array([[100, 100], [200, 100], [200, 200], [100, 200]])
FRAME_RESOLUTION = (300, 300)


@pytest.mark.parametrize(
    "detections, polygon_zone, expected_results, exception",
    [
        (
            DETECTIONS,
            sv.PolygonZone(
                POLYGON,
                FRAME_RESOLUTION,
                triggering_anchors=(
                    sv.Position.TOP_LEFT,
                    sv.Position.TOP_RIGHT,
                    sv.Position.BOTTOM_LEFT,
                    sv.Position.BOTTOM_RIGHT,
                ),
            ),
            np.array(
                [False, False, False, True, True, True, False, False, False], dtype=bool
            ),
            DoesNotRaise(),
        ),  # Test all four corners
        (
            DETECTIONS,
            sv.PolygonZone(
                POLYGON,
                FRAME_RESOLUTION,
            ),
            np.array(
                [False, False, True, True, True, True, False, False, False], dtype=bool
            ),
            DoesNotRaise(),
        ),  # Test default behaviour when no anchors are provided
        (
            DETECTIONS,
            sv.PolygonZone(
                POLYGON, FRAME_RESOLUTION, triggering_position=sv.Position.BOTTOM_CENTER
            ),
            np.array(
                [False, False, True, True, True, True, False, False, False], dtype=bool
            ),
            DoesNotRaise(),
        ),  # Test default behaviour with deprecated api.
        (
            sv.Detections.empty(),
            sv.PolygonZone(
                POLYGON,
                FRAME_RESOLUTION,
            ),
            np.array([], dtype=bool),
            DoesNotRaise(),
        ),  # Test empty detections
    ],
)
def test_polygon_zone_trigger(
    detections: sv.Detections,
    polygon_zone: sv.PolygonZone,
    expected_results: np.ndarray,
    exception: Exception,
) -> None:
    with exception:
        in_zone = polygon_zone.trigger(detections)
        assert np.all(in_zone == expected_results)
