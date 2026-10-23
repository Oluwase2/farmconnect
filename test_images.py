"""Run with:  python -m unittest -v test_images"""
import base64, os, re, tempfile, unittest
import artwork, images


def decode_svg(html):
    uri = re.search(r"data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)", html).group(1)
    return base64.b64decode(uri).decode()


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_every_produce_has_its_own_illustration(self):
        names = ["Maize", "Cassava", "Yam", "Tomatoes", "Pepper", "Rice", "Beans", "Onions"]
        svgs = {n: decode_svg(images.produce_img_html(n, 100, self.d)) for n in names}
        self.assertEqual(len(set(svgs.values())), len(names))
        for s in svgs.values():
            self.assertTrue(s.startswith("<svg") and s.endswith("</svg>"))

    def test_other_produce_gets_default_basket(self):
        self.assertEqual(decode_svg(images.produce_img_html("Sweet Potato", 100, self.d)), artwork.other())

    def test_photo_overrides_illustration(self):
        with open(os.path.join(self.d, "maize.jpg"), "wb") as f:
            f.write(b"\xff\xd8\xff fake")
        html = images.produce_img_html("Maize", 120, self.d)
        self.assertIn("data:image/jpeg;base64,", html)
        self.assertNotIn("image/svg", html)

    def test_name_matching_ignores_case_and_spaces(self):
        with open(os.path.join(self.d, "sweetpotato.png"), "wb") as f:
            f.write(b"x")
        self.assertIsNotNone(images.find_image("Sweet Potato", self.d))

    def test_hero(self):
        self.assertIn("image/svg+xml", images.hero_style(self.d))
        with open(os.path.join(self.d, "hero.webp"), "wb") as f:
            f.write(b"x")
        self.assertIn("image/webp", images.hero_style(self.d))


if __name__ == "__main__":
    unittest.main()
