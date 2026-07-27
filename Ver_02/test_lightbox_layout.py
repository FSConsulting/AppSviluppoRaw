import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from app_gui import calcola_layout_lightbox


class TestLightboxLayout(unittest.TestCase):
    def test_scrollregion_expands_to_cover_centered_zoomed_image(self):
        x_pos, y_pos, scrollregion = calcola_layout_lightbox(
            canvas_w=800,
            canvas_h=600,
            img_w=1000,
            img_h=700,
            focus_x=0.5,
            focus_y=0.5,
            zoom_attivo=True,
        )

        self.assertEqual(x_pos, -100)
        self.assertEqual(y_pos, -50)
        self.assertEqual(scrollregion, (-100, -50, 900, 650))

    def test_scrollregion_stays_centered_for_smaller_images(self):
        x_pos, y_pos, scrollregion = calcola_layout_lightbox(
            canvas_w=1200,
            canvas_h=800,
            img_w=500,
            img_h=400,
            focus_x=0.5,
            focus_y=0.5,
            zoom_attivo=False,
        )

        self.assertEqual(x_pos, 350)
        self.assertEqual(y_pos, 200)
        self.assertEqual(scrollregion, (0, 0, 1200, 800))


if __name__ == '__main__':
    unittest.main()
