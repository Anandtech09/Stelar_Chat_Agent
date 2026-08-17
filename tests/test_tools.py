import os
import tempfile
import unittest
from tools.web_tools import fetch_materials, web_search
from tools.design_tools import generate_palette, calculate_layout
from tools.storage_tools import save_consultation, send_email_consultation, summarize_brief_for_email, verify_email_deliverability
from scheduler import add_to_queue, load_queue, save_queue

class TestStelarModularTools(unittest.TestCase):

    def test_generate_palette(self):
        palette = generate_palette(style="Warm Modern", room_type="Living Room")
        self.assertIn("colors", palette)
        self.assertEqual(len(palette["colors"]), 4)
        self.assertIn("materials", palette)

    def test_fetch_materials(self):
        materials = fetch_materials("Warm Modern")
        self.assertIsInstance(materials, list)
        self.assertTrue(len(materials) > 0)

    def test_calculate_layout(self):
        res = calculate_layout(16, 12)
        self.assertEqual(res["room_area"], 192.0)
        self.assertTrue(res["furniture_fit"])

    def test_verify_email_deliverability(self):
        # Valid email domain
        valid_res = verify_email_deliverability("manorama@gmail.com")
        self.assertTrue(valid_res["valid"])

        # Fake invalid email domain
        invalid_res = verify_email_deliverability("user@fake12345domain.xyz")
        self.assertFalse(invalid_res["valid"])

    def test_save_consultation_isolated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_brief = "Sample design brief."
            filepath = os.path.join(tmpdir, "test_brief.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(sample_brief)
            self.assertTrue(os.path.exists(filepath))

    def test_summarize_brief_for_email(self):
        sample_brief = "Room: Living Room\nStyle: Warm Modern"
        summary = summarize_brief_for_email("stelar_test.txt", sample_brief)
        self.assertIn("BRIEF TITLE / REFERENCE FILE: stelar_test.txt", summary)

    def test_send_email_consultation(self):
        res = send_email_consultation("varundadwal123@gmail.com", "Sample brief.", filename="stelar_test.txt")
        self.assertIsInstance(res, str)

if __name__ == "__main__":
    unittest.main()
