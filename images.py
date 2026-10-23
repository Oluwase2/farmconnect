"""Produce pictures for FarmConnect. No Streamlit code here so it can be tested alone.
Order of preference: 1) your own photo in the 'images' folder (e.g. maize.jpg), 2) the built-in illustration."""
import base64
from functools import lru_cache
from pathlib import Path

import artwork

IMG_DIR = Path(__file__).with_name("images")
EXTS = (".jpg", ".jpeg", ".png", ".webp")
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


def _key(name):
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


def find_image(name, img_dir=None):
    folder = Path(img_dir) if img_dir else IMG_DIR
    key = _key(name)
    if key and folder.is_dir():
        for ext in EXTS:
            p = folder / (key + ext)
            if p.is_file():
                return p
    return None


@lru_cache(maxsize=64)
def _file_uri(path_str, mtime):
    p = Path(path_str)
    return f"data:{MIME[p.suffix.lower()]};base64," + base64.b64encode(p.read_bytes()).decode()


@lru_cache(maxsize=64)
def _svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _uri_for(name, img_dir=None):
    p = find_image(name, img_dir)
    if p:
        try:
            return _file_uri(str(p), p.stat().st_mtime)
        except OSError:
            pass
    return _svg_uri(artwork.svg_for(_key(name)))


def produce_img_html(name, height=150, img_dir=None):
    return (f"<img src='{_uri_for(name, img_dir)}' alt='{_key(name)}' style='width:100%;height:{height}px;"
            "object-fit:cover;border-radius:10px;display:block'>")


def hero_style(img_dir=None):
    """Inline CSS for the marketplace banner: your hero photo if present, else the built-in farm scene."""
    p = find_image("hero", img_dir)
    uri = None
    if p:
        try:
            uri = _file_uri(str(p), p.stat().st_mtime)
        except OSError:
            uri = None
    if uri is None:
        uri = _svg_uri(artwork.hero_svg())
    return (f"background-image:linear-gradient(rgba(27,94,32,.80),rgba(46,125,50,.45)),url('{uri}');"
            "background-size:cover;background-position:center;")
