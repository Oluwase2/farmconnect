"""FarmConnect database layer (SQLite) and input validation.
No Streamlit code lives here, so it can be tested on its own."""
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("farmconnect.db")
UNITS = ["kg", "tonnes", "bags", "baskets", "crates", "pieces"]
PRODUCE = ["Maize", "Cassava", "Yam", "Tomatoes", "Pepper", "Rice", "Beans", "Onions", "Other"]


class DBError(Exception):
    """Friendly database error that is safe to show to users."""


@contextmanager
def connect(path=None):
    conn = sqlite3.connect(str(path or DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise DBError("A database problem occurred. Nothing was saved. Please try again.") from exc
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT UNIQUE,
    produce TEXT NOT NULL,
    location TEXT NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    unit TEXT NOT NULL,
    price_per_unit REAL NOT NULL CHECK (price_per_unit > 0),
    phone TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
    is_demo INTEGER NOT NULL DEFAULT 0,
    submission_token TEXT UNIQUE
);
"""

# Fictional demonstration records. Phone numbers are NOT real farmers.
DEMO = [
    ("Maize", "Ibadan, Oyo State", 50, "bags", 38000, "08000000001"),
    ("Cassava", "Abeokuta, Ogun State", 2, "tonnes", 120000, "08000000002"),
    ("Tomatoes", "Jos, Plateau State", 40, "baskets", 15000, "08000000003"),
    ("Rice", "Kano, Kano State", 30, "bags", 65000, "08000000004"),
    ("Yam", "Makurdi, Benue State", 500, "pieces", 1800, "08000000005"),
]


def init_db(path=None, seed=True):
    with connect(path) as c:
        c.executescript(SCHEMA)
        count = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    if seed and count == 0:
        seed_demo(path)


# ---------- validation ----------
def parse_positive(text, what="value"):
    """Return float > 0 or raise ValueError with a friendly message."""
    cleaned = str(text or "").strip().replace(",", "").replace("₦", "")
    if not cleaned:
        raise ValueError(f"Please enter the {what}.")
    try:
        val = float(cleaned)
    except ValueError:
        raise ValueError(f"The {what} must be a number, e.g. 1500.")
    if val != val or val in (float("inf"), float("-inf")) or val <= 0:
        raise ValueError(f"The {what} must be greater than zero.")
    return val


def normalize_phone(text):
    """Accept 08012345678, 8012345678, 2348012345678, +234 801 234 5678.
    Returns 11-digit local format as TEXT (leading zero kept)."""
    digits = re.sub(r"[\s\-().]", "", str(text or ""))
    if digits.startswith("+"):
        digits = digits[1:]
    if not digits.isdigit():
        raise ValueError("Phone number may only contain digits (and an optional + at the start).")
    if digits.startswith("234") and len(digits) == 13:
        digits = "0" + digits[3:]
    elif len(digits) == 10 and digits[0] in "789":
        digits = "0" + digits
    if not re.fullmatch(r"0[789]\d{9}", digits):
        raise ValueError("Enter a valid Nigerian mobile number, e.g. 08012345678 or +2348012345678.")
    return digits


def whatsapp_number(phone):
    return "234" + phone[1:]


# ---------- operations ----------
def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_listing(produce, location, quantity, unit, price, phone, token=None, is_demo=False, path=None):
    """Validate and save. Returns the saved row. A repeated token returns the
    existing record instead of creating a duplicate."""
    produce, location = (produce or "").strip(), (location or "").strip()
    if not produce:
        raise ValueError("Produce name is missing.")
    if not location:
        raise ValueError("Location is missing.")
    if unit not in UNITS:
        raise ValueError("Please choose a valid unit.")
    quantity = parse_positive(quantity, "quantity")
    price = parse_positive(price, "price")
    phone = normalize_phone(phone)
    with connect(path) as c:
        if token:
            row = c.execute("SELECT * FROM listings WHERE submission_token=?", (token,)).fetchone()
            if row:
                return dict(row)
        cur = c.execute(
            "INSERT INTO listings (produce, location, quantity, unit, price_per_unit, phone,"
            " created_at, status, is_demo, submission_token) VALUES (?,?,?,?,?,?,?,'active',?,?)",
            (produce.title(), location, quantity, unit, price, phone, _now(), int(is_demo), token),
        )
        lid = cur.lastrowid
        ref = f"{'DM' if is_demo else 'FC'}{lid:04d}"
        c.execute("UPDATE listings SET reference=? WHERE id=?", (ref, lid))
        row = c.execute("SELECT * FROM listings WHERE id=?", (lid,)).fetchone()
    return dict(row)


def get_listing(listing_id, path=None):
    with connect(path) as c:
        row = c.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
    return dict(row) if row else None


def search_listings(query="", produce="All", location="All", active_only=True, path=None):
    sql, args = "SELECT * FROM listings WHERE 1=1", []
    if active_only:
        sql += " AND status='active'"
    if produce and produce != "All":
        sql += " AND produce=?"; args.append(produce)
    if location and location != "All":
        sql += " AND location=?"; args.append(location)
    if query and query.strip():
        like = f"%{query.strip()}%"
        sql += " AND (produce LIKE ? OR location LIKE ? OR reference LIKE ?)"
        args += [like, like, like]
    sql += " ORDER BY created_at DESC, id DESC"
    with connect(path) as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def distinct_values(column, path=None):
    assert column in ("produce", "location")
    with connect(path) as c:
        rows = c.execute(f"SELECT DISTINCT {column} FROM listings WHERE status='active' ORDER BY {column}").fetchall()
    return [r[0] for r in rows]


def stats(path=None):
    with connect(path) as c:
        total = c.execute("SELECT COUNT(*) FROM listings WHERE status='active'").fetchone()[0]
        kinds = c.execute("SELECT COUNT(DISTINCT produce) FROM listings WHERE status='active'").fetchone()[0]
    return total, kinds


def set_status(listing_id, status, path=None):
    if status not in ("active", "inactive"):
        raise ValueError("Invalid status.")
    with connect(path) as c:
        c.execute("UPDATE listings SET status=? WHERE id=?", (status, listing_id))


def delete_listing(listing_id, path=None):
    with connect(path) as c:
        c.execute("DELETE FROM listings WHERE id=?", (listing_id,))


def seed_demo(path=None):
    with connect(path) as c:
        existing = c.execute("SELECT COUNT(*) FROM listings WHERE is_demo=1").fetchone()[0]
    if existing:
        return 0
    for p, loc, q, u, pr, ph in DEMO:
        add_listing(p, loc, q, u, pr, ph, is_demo=True, path=path)
    return len(DEMO)


def clear_demo(path=None):
    """Deletes ONLY records flagged is_demo=1. Real listings are untouched."""
    with connect(path) as c:
        return c.execute("DELETE FROM listings WHERE is_demo=1").rowcount
