# 🌾 FarmConnect (prototype, version 2)

A prototype agricultural marketplace for Nigeria. Farmers list produce through a **simulated USSD session**; buyers browse
the marketplace (with pictures of each produce) and contact farmers directly. No telephony, SMS, payment or API keys are used.

## Run it (Windows)
1. Open this folder, click the address bar, type `cmd`, press Enter.
2. `python -m pip install -r requirements.txt`
3. `python -m streamlit run app.py`
4. The app opens at http://localhost:8501. Stop it with `Ctrl + C`.

Admin password for **Manage Listings**: `farmconnect` when running locally. When deployed, set `ADMIN_PASSWORD` in the
host's Secrets (see `.streamlit/secrets.toml.example`).

## Pictures
Each produce shows a built-in illustration automatically. To use your own photos, put them in `images/` named after the
produce (`maize.jpg`, `rice.png`, ...); `hero.jpg` is an optional banner. See `images/README.txt`.

## Files
`app.py` interface · `db.py` database + validation · `images.py` / `artwork.py` pictures · `test_db.py`, `test_images.py` tests

## Tests
`python -m unittest -v test_db test_images`

## Demo script
Simulator → sell produce → fill the steps → submit → note the reference → View in marketplace → Contact Farmer.
Manage Listings → deactivate / reactivate / delete → reset sample data.

## Notes
USSD/SMS are simulated. A hosted copy may lose its SQLite data when it restarts; sample listings are re-created automatically.
Farmer phone numbers are personal data; demo numbers are fictional.
