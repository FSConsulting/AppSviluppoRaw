import os
import sys
import unittest
from PIL import Image

# Assicura che il modulo Ver_02 sia importabile quando si esegue il test dalla cartella Ver_02
sys.path.insert(0, os.path.dirname(__file__))

from ritocco_manager import RitoccoManager


class DummySlider:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


class DummyApp:
    def __init__(self, width=300, height=200, rotation=0.0, crop=0.0, margine=0.0):
        self.img_anteprima_base = Image.new('RGB', (400, 300), color='white')
        self.sld_rotation = DummySlider(rotation)
        self.sld_crop = DummySlider(crop)
        self.sld_margine = DummySlider(margine)
        self.w_visualizzato = width
        self.h_visualizzato = height


class TestRitoccoManagerTransformations(unittest.TestCase):
    def assertPointsAlmostEqual(self, point_a, point_b, tol=1e-5):
        self.assertAlmostEqual(point_a[0], point_b[0], delta=tol)
        self.assertAlmostEqual(point_a[1], point_b[1], delta=tol)

    def test_native_to_screen_and_back_no_rotation_no_crop(self):
        app = DummyApp(rotation=0.0, crop=0.0, margine=0.0)
        manager = RitoccoManager(app)

        native_point = (80.0, 120.0)
        screen_point = manager.native_to_screen_coords(*native_point)
        native_back = manager.traduci_schermo_a_pixel_nativo(*screen_point)

        self.assertPointsAlmostEqual(native_point, native_back)

    def test_native_to_screen_and_back_with_rotation(self):
        app = DummyApp(rotation=30.0, crop=0.0, margine=0.0)
        manager = RitoccoManager(app)

        native_point = (200.0, 150.0)
        screen_point = manager.native_to_screen_coords(*native_point)
        native_back = manager.traduci_schermo_a_pixel_nativo(*screen_point)

        self.assertPointsAlmostEqual(native_point, native_back)

    def test_native_to_screen_and_back_with_crop_and_margine(self):
        app = DummyApp(rotation=-45.0, crop=10.0, margine=5.0)
        manager = RitoccoManager(app)

        native_point = (120.0, 80.0)
        screen_point = manager.native_to_screen_coords(*native_point)
        native_back = manager.traduci_schermo_a_pixel_nativo(*screen_point)

        self.assertPointsAlmostEqual(native_point, native_back)

    def test_screen_point_is_inside_visible_bounds_with_transforms(self):
        app = DummyApp(rotation=15.0, crop=20.0, margine=10.0)
        manager = RitoccoManager(app)

        native_point = (250.0, 200.0)
        screen_x, screen_y = manager.native_to_screen_coords(*native_point)

        self.assertGreaterEqual(screen_x, 0.0)
        self.assertGreaterEqual(screen_y, 0.0)
        self.assertLessEqual(screen_x, app.w_visualizzato)
        self.assertLessEqual(screen_y, app.h_visualizzato)


if __name__ == '__main__':
    unittest.main()
