#!/usr/bin/env python
"""
Unit tests for ship_callsign functions

author: Besnard, Laurent
"""

import unittest

from aodncore.testlib import BaseTestCase
from aodndata.soop.ship_callsign import ship_callsign
from mock import patch


def mock_platform_altlabels_per_preflabel(category_name='Vessel'):
    return {'VLHJ': 'Southern-Surveyor',
            '9V2768': 'RTM-Wakmatha',
            '3FLZ': 'Tropical-Islander'}


class TestShipCallSign(BaseTestCase):
    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_ship_name(self, mock_ship):
        self.assertEqual(ship_callsign('3FLZ'), 'Tropical-Islander')

    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_unknown_ship_name(self, mock_ship):
        self.assertEqual(ship_callsign('unknown'), None)


if __name__ == '__main__':
    unittest.main()
