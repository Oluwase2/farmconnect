"""Run with:  python -m unittest -v test_db   (no extra installs needed)"""
import os, tempfile, unittest
import db


class DBTests(unittest.TestCase):
    def setUp(self):
        self.p = os.path.join(tempfile.mkdtemp(), "t.db")
        db.init_db(self.p)

    def test_seed_and_stats(self):
        self.assertEqual(db.stats(self.p), (5, 5))
        for r in db.search_listings(path=self.p):
            self.assertEqual(r["is_demo"], 1)
            self.assertTrue(r["reference"].startswith("DM"))

    def test_add_and_visible(self):
        r = db.add_listing("maize", "Ibadan, Oyo State", "10", "bags", "₦1,500", "+234 803 123 4567", token="t1", path=self.p)
        self.assertTrue(r["reference"].startswith("FC"))
        self.assertEqual(r["phone"], "08031234567")
        self.assertEqual(r["status"], "active")
        self.assertEqual(db.get_listing(r["id"], self.p)["phone"], "08031234567")
        self.assertTrue(any(x["id"] == r["id"] for x in db.search_listings("Maize", path=self.p)))

    def test_duplicate_token(self):
        a = db.add_listing("Yam", "Jos", 5, "pieces", 100, "08031234567", token="same", path=self.p)
        b = db.add_listing("Yam", "Jos", 5, "pieces", 100, "08031234567", token="same", path=self.p)
        self.assertEqual(a["id"], b["id"])
        self.assertEqual(db.stats(self.p)[0], 6)

    def test_validation(self):
        for q, pr, ph in [("0", "10", "08031234567"), ("abc", "10", "08031234567"), ("5", "-1", "08031234567"),
                          ("5", "10", "12345"), ("5", "10", "0603123456x"), ("nan", "10", "08031234567")]:
            with self.assertRaises(ValueError):
                db.add_listing("Rice", "Kano", q, "kg", pr, ph, path=self.p)
        with self.assertRaises(ValueError):
            db.add_listing("", "Kano", 1, "kg", 1, "08031234567", path=self.p)
        self.assertEqual(db.stats(self.p)[0], 5)

    def test_phone_formats(self):
        for s in ["08031234567", "8031234567", "2348031234567", "+2348031234567", "0803 123 4567"]:
            self.assertEqual(db.normalize_phone(s), "08031234567")

    def test_status_delete_and_clear_demo(self):
        r = db.add_listing("Beans", "Kano", 1, "bags", 50000, "09031234567", path=self.p)
        db.set_status(r["id"], "inactive", self.p)
        self.assertFalse(any(x["id"] == r["id"] for x in db.search_listings(path=self.p)))
        self.assertTrue(any(x["id"] == r["id"] for x in db.search_listings(active_only=False, path=self.p)))
        db.set_status(r["id"], "active", self.p)
        self.assertEqual(db.clear_demo(self.p), 5)
        self.assertIsNotNone(db.get_listing(r["id"], self.p))
        db.delete_listing(r["id"], self.p)
        self.assertIsNone(db.get_listing(r["id"], self.p))
        self.assertIsNone(db.get_listing(9999, self.p))


if __name__ == "__main__":
    unittest.main()
