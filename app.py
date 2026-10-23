"""FarmConnect - prototype agricultural marketplace with a simulated USSD flow.
Run with:  streamlit run app.py"""
import hmac
import uuid
import streamlit as st
import db
import images

st.set_page_config(page_title="FarmConnect", page_icon="🌾", layout="wide")

CSS = """
<style>
.fc-hero{background:linear-gradient(135deg,#1b5e20,#43a047);color:#fff;padding:1.4rem 1.6rem;border-radius:14px;margin-bottom:1rem}
.fc-hero h1{margin:0;font-size:2rem;color:#fff}.fc-hero p{margin:.3rem 0 0;opacity:.95}
.fc-badge{background:#fff3cd;color:#7a5b00;padding:2px 8px;border-radius:10px;font-size:.75rem;font-weight:600}
.fc-price{color:#1b5e20;font-weight:700;font-size:1.1rem}
.fc-muted{color:#666;font-size:.85rem}
.ussd{background:#0b0f0c;color:#7CFC00;font-family:'Courier New',monospace;border:3px solid #333;border-radius:22px;
 padding:1rem 1.1rem;max-width:380px;margin:0 auto .8rem;min-height:220px;white-space:pre-wrap;font-size:.95rem}
.ussd-status{color:#9e9e9e;font-size:.75rem;border-bottom:1px solid #333;padding-bottom:.4rem;margin-bottom:.6rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- helpers ----------
def naira(x):
    return f"₦{x:,.2f}".replace(".00", "")

def qty(x):
    return f"{x:g}"

def safe(fn, *a, **k):
    """Run a DB call; show a friendly error instead of a stack trace."""
    try:
        return fn(*a, **k), None
    except db.DBError as e:
        return None, str(e)
    except ValueError as e:
        return None, str(e)
    except Exception:
        return None, "Something went wrong. Please try again."

def go(page):
    st.session_state.page = page

try:
    db.init_db()
except Exception:
    st.error("Could not open the database. Check that the app folder is writable.")
    st.stop()

PAGES = ["🛒 Marketplace", "📱 Farmer USSD Simulator", "🗂️ Manage Listings", "ℹ️ About & Future Integration"]
st.session_state.setdefault("page", PAGES[0])
st.session_state.setdefault("detail_id", None)
st.session_state.setdefault("show_contact", False)

st.sidebar.markdown("## 🌾 FarmConnect")
st.sidebar.radio("Navigate", PAGES, key="page")
st.sidebar.caption("Prototype · simulated USSD · no real telephony")

# ---------- Marketplace ----------
def contact_panel(r):
    st.success("Farmer contact (for listing " + r["reference"] + ")")
    st.markdown(f"### 📞 {r['phone']}")
    wa = f"https://wa.me/{db.whatsapp_number(r['phone'])}?text=" + \
         f"Hello, I saw your {r['produce']} listing ({r['reference']}) on FarmConnect."
    c1, c2 = st.columns(2)
    c1.link_button("📞 Call farmer", f"tel:{r['phone']}", use_container_width=True)
    c2.link_button("💬 WhatsApp", wa, use_container_width=True)
    st.info("Buyers and farmers negotiate directly. FarmConnect does not handle payments, delivery "
            "or transactions, and does not verify quality, availability or ownership.")

def show_detail(lid):
    r, err = safe(db.get_listing, lid)
    if err or not r or r["status"] != "active":
        st.warning(err or "This listing is no longer available.")
        st.button("← Back to marketplace", on_click=lambda: st.session_state.update(detail_id=None, show_contact=False))
        return
    st.button("← Back to marketplace", on_click=lambda: st.session_state.update(detail_id=None, show_contact=False))
    st.markdown(f"## {r['produce']}" + ("  <span class='fc-badge'>SAMPLE DATA</span>" if r["is_demo"] else ""),
                unsafe_allow_html=True)
    st.markdown(images.produce_img_html(r["produce"], 240), unsafe_allow_html=True)
    a, b = st.columns(2)
    a.markdown(f"**Location:** {r['location']}  \n**Quantity:** {qty(r['quantity'])} {r['unit']}  \n"
               f"**Price per {r['unit']}:** {naira(r['price_per_unit'])}")
    b.markdown(f"**Listing reference:** {r['reference']}  \n**Date listed:** {r['created_at']}  \n"
               f"**Total asking value:** {naira(r['quantity'] * r['price_per_unit'])}")
    st.caption("The price is the farmer's asking price, not a verified market price. Quality, availability "
               "and ownership have not been independently verified.")
    if r["is_demo"]:
        st.warning("Demonstration listing: fictional record, not a real farmer or offer.")
    if st.button("📞 Contact Farmer", type="primary"):
        st.session_state.show_contact = True
    if st.session_state.show_contact:
        contact_panel(r)

def open_listing(lid, contact=False):
    st.session_state.detail_id = lid
    st.session_state.show_contact = contact

def marketplace():
    total, kinds = db.stats()
    st.markdown(f"<div class='fc-hero' style=\"{images.hero_style()}\"><h1>🌾 FarmConnect</h1><p>A prototype marketplace that connects "
                "smallholder farmers with produce buyers across Nigeria — farmers list produce through a "
                "simple USSD-style flow, buyers contact them directly.</p></div>", unsafe_allow_html=True)
    if st.session_state.detail_id is not None:
        show_detail(st.session_state.detail_id)
        return
    m1, m2 = st.columns(2)
    m1.metric("Active listings", total)
    m2.metric("Produce types", kinds)
    q = st.text_input("🔎 Search", placeholder="Search produce, location or reference (e.g. FC0006)")
    f1, f2 = st.columns(2)
    prod = f1.selectbox("Produce type", ["All"] + db.distinct_values("produce"))
    loc = f2.selectbox("Location", ["All"] + db.distinct_values("location"))
    rows, err = safe(db.search_listings, q, prod, loc)
    if err:
        st.error(err); return
    if not rows:
        st.info("No listings match your search. Try clearing the filters.")
        return
    cols = st.columns(3)
    for i, r in enumerate(rows):
        with cols[i % 3].container(border=True):
            st.markdown(images.produce_img_html(r["produce"], 140), unsafe_allow_html=True)
            st.markdown(f"**{r['produce']}**" + ("  <span class='fc-badge'>SAMPLE DATA</span>" if r["is_demo"] else ""),
                        unsafe_allow_html=True)
            st.markdown(f"📍 {r['location']}  \n📦 {qty(r['quantity'])} {r['unit']}")
            st.markdown(f"<span class='fc-price'>{naira(r['price_per_unit'])} per {r['unit']}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='fc-muted'>Ref {r['reference']} · Listed {r['created_at'][:10]}</span>", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            b1.button("View details", key=f"v{r['id']}", on_click=open_listing, args=(r["id"],), use_container_width=True)
            b2.button("Contact Farmer", key=f"c{r['id']}", on_click=open_listing, args=(r["id"], True),
                      type="primary", use_container_width=True)

# ---------- USSD simulator ----------
def new_session():
    st.session_state.ussd = {"step": "welcome", "data": {}, "token": uuid.uuid4().hex, "ref": None, "msg": None}

def ussd_screen(text, status="Session active"):
    st.markdown(f"<div class='ussd'><div class='ussd-status'>● {status} · *384*FARM#</div>{text}</div>",
                unsafe_allow_html=True)

def ussd():
    st.header("📱 Farmer USSD Simulator")
    st.caption("Simulates a farmer's USSD session locally. No telephony, SMS or internet service is used.")
    if "ussd" not in st.session_state:
        new_session()
    s = st.session_state.ussd
    d, step = s["data"], s["step"]
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if s["msg"]:
            st.error(s["msg"]); s["msg"] = None

        def advance(nxt, **vals):
            d.update(vals); s["step"] = nxt; st.rerun()

        if step == "welcome":
            ussd_screen("WELCOME TO FARMCONNECT\n\n1. Sell your produce\n2. Exit")
            with st.form("f_welcome"):
                c = st.radio("Choose an option", ["1. Sell your produce", "2. Exit"])
                if st.form_submit_button("Send", use_container_width=True):
                    advance("location" if c.startswith("1") else "exit")
        elif step == "location":
            ussd_screen("Enter your farm or produce location.\n\nExample: Ibadan, Oyo State")
            with st.form("f_loc"):
                v = st.text_input("Location", placeholder="Ibadan, Oyo State")
                if st.form_submit_button("Send", use_container_width=True):
                    if len(v.strip()) < 2:
                        s["msg"] = "Please enter your location."; st.rerun()
                    advance("produce", location=v.strip())
        elif step == "produce":
            ussd_screen("What produce do you want to sell?\n\n" + "\n".join(f"{i+1}. {p}" for i, p in enumerate(db.PRODUCE)))
            with st.form("f_prod"):
                p = st.selectbox("Produce", db.PRODUCE)
                other = st.text_input("If 'Other', enter the produce name")
                if st.form_submit_button("Send", use_container_width=True):
                    name = other.strip() if p == "Other" else p
                    if not name:
                        s["msg"] = "Please enter the produce name."; st.rerun()
                    advance("quantity", produce=name)
        elif step == "quantity":
            ussd_screen(f"How much {d['produce']} is available?\n\nEnter quantity and choose a unit.")
            with st.form("f_qty"):
                q = st.text_input("Quantity", placeholder="e.g. 20")
                u = st.selectbox("Unit", db.UNITS)
                if st.form_submit_button("Send", use_container_width=True):
                    _, err = safe(db.parse_positive, q, "quantity")
                    if err:
                        s["msg"] = err; st.rerun()
                    advance("price", quantity=q, unit=u)
        elif step == "price":
            ussd_screen(f"Enter your asking price PER {d['unit'].upper()} in Naira.\n\nExample: 1500 (₦1,500 per {d['unit']})")
            with st.form("f_price"):
                p = st.text_input(f"Price per {d['unit']} (₦)", placeholder="1500")
                if st.form_submit_button("Send", use_container_width=True):
                    _, err = safe(db.parse_positive, p, "price")
                    if err:
                        s["msg"] = err; st.rerun()
                    advance("phone", price=p)
        elif step == "phone":
            ussd_screen("Enter your contact phone number.\n\nExample: 08031234567")
            st.caption("Prototype note: your number is shown only to buyers who tap Contact Farmer.")
            with st.form("f_phone"):
                p = st.text_input("Phone number", placeholder="08031234567")
                if st.form_submit_button("Send", use_container_width=True):
                    try:
                        advance("review", phone=db.normalize_phone(p))
                    except ValueError as e:
                        s["msg"] = str(e); st.rerun()
        elif step == "review":
            ussd_screen(f"FARMCONNECT LISTING SUMMARY\n\nLocation: {d['location']}\nProduce: {d['produce']}\n"
                        f"Quantity: {d['quantity']}\nUnit: {d['unit']}\n"
                        f"Price per unit: {naira(float(d['price'].replace(',', '').replace('₦', '')))} per {d['unit']}\n"
                        f"Farmer contact: {d['phone']}\n\n1. Submit listing\n2. Cancel")
            with st.form("f_review"):
                c = st.radio("Choose an option", ["1. Submit listing", "2. Cancel"])
                if st.form_submit_button("Send", use_container_width=True):
                    if c.startswith("2"):
                        advance("cancelled")
                    row, err = safe(db.add_listing, d["produce"], d["location"], d["quantity"], d["unit"],
                                    d["price"], d["phone"], s["token"])
                    if err:
                        s["msg"] = "Listing NOT saved. " + err; st.rerun()
                    s["ref"], s["lid"] = row["reference"], row["id"]
                    advance("done")
        elif step == "done":
            ussd_screen(f"LISTING SUBMITTED\n\nYour listing reference: {s['ref']}\n\nThank you for using FarmConnect.", "Session ended")
            st.success(f"Saved! Listing reference {s['ref']} is now live on the marketplace.")
            c1, c2 = st.columns(2)
            c1.button("🛒 View in marketplace", on_click=lambda: (go(PAGES[0]), open_listing(s["lid"])), type="primary", use_container_width=True)
            c2.button("Start new session", on_click=new_session, use_container_width=True)
        elif step in ("exit", "cancelled"):
            ussd_screen("Thank you for using FarmConnect.\nGoodbye." if step == "exit" else "Listing cancelled. Nothing was saved.\nGoodbye.", "Session ended")
            st.button("Start new session", on_click=new_session, use_container_width=True)

# ---------- Manage ----------
def admin_password():
    """Password comes from Streamlit secrets (ADMIN_PASSWORD). If none is set
    (e.g. running locally), fall back to a demo password."""
    try:
        return str(st.secrets["ADMIN_PASSWORD"]), True
    except Exception:
        return "farmconnect", False

def manage():
    st.header("🗂️ Manage Listings")
    pw, from_secret = admin_password()
    if not st.session_state.get("admin_ok"):
        st.info("This page is for the prototype administrator. Enter the password to continue.")
        with st.form("f_login"):
            entered = st.text_input("Admin password", type="password")
            if st.form_submit_button("Unlock"):
                if hmac.compare_digest(entered.encode(), pw.encode()):
                    st.session_state.admin_ok = True
                    st.rerun()
                st.error("Incorrect password.")
        if not from_secret:
            st.caption("No ADMIN_PASSWORD secret is set, so the demo password 'farmconnect' is in use. "
                       "Set a secret before sharing this app publicly.")
        return
    st.button("🔒 Lock admin page", on_click=lambda: st.session_state.update(admin_ok=False))
    rows, err = safe(db.search_listings, active_only=False)
    if err:
        st.error(err); return
    if not rows:
        st.info("No listings yet."); return
    st.caption("Prototype admin view: no login. A production version would restrict who can edit or delete listings.")
    for r in rows:
        with st.container(border=True):
            c1, c2 = st.columns([3, 2])
            tag = "🟢 Active" if r["status"] == "active" else "⚪ Inactive"
            demo = " · SAMPLE DATA" if r["is_demo"] else ""
            c1.markdown(f"**{r['reference']}** · {r['produce']} · {r['location']}  \n"
                        f"{qty(r['quantity'])} {r['unit']} @ {naira(r['price_per_unit'])}/{r['unit']} · {tag}{demo}  \n"
                        f"<span class='fc-muted'>Listed {r['created_at']}</span>", unsafe_allow_html=True)
            with c2:
                new = "inactive" if r["status"] == "active" else "active"
                if st.button("Deactivate" if new == "inactive" else "Reactivate", key=f"s{r['id']}"):
                    _, e = safe(db.set_status, r["id"], new)
                    st.error(e) if e else st.rerun()
                if st.checkbox("Confirm delete", key=f"k{r['id']}"):
                    if st.button("🗑️ Delete permanently", key=f"d{r['id']}"):
                        _, e = safe(db.delete_listing, r["id"])
                        st.error(e) if e else st.rerun()
    st.divider()
    st.subheader("Demonstration data")
    a, b = st.columns(2)
    if a.button("Reload sample listings"):
        n, e = safe(db.seed_demo)
        st.error(e) if e else st.rerun()
    if b.checkbox("Confirm clear sample data") and b.button("Clear sample data only"):
        n, e = safe(db.clear_demo)
        st.error(e) if e else st.rerun()
    st.caption("Clearing sample data never touches listings created through the simulator.")

# ---------- About ----------
def about():
    st.header("ℹ️ About & Future USSD/SMS Integration")
    st.subheader("Future USSD/SMS Integration")
    st.markdown("""
The current interface **simulates** the farmer's interaction locally. No real USSD, SMS, payment or telephony service exists in this prototype, and no API keys are needed.

In a future implementation, a telephony provider could receive the farmer's USSD responses, forward the session data to a backend endpoint, and let the backend validate and save the listing using the same database logic used here. If SMS confirmation were added, the backend could text the farmer their listing reference.
""")
    st.subheader("Privacy")
    st.markdown("Farmer phone numbers are personal information. They are shown only after a buyer taps *Contact Farmer*. "
                "Demonstration numbers are fictional. A production version would need a privacy policy and a consent process.")
    st.subheader("Scope")
    st.markdown("FarmConnect only connects buyers and sellers. It does not process payments, arrange delivery, or verify prices, quality, availability or ownership.")

page = st.session_state.page
{PAGES[0]: marketplace, PAGES[1]: ussd, PAGES[2]: manage, PAGES[3]: about}[page]()
