import streamlit as st
import sqlite3
from pathlib import Path
from datetime import date, datetime
from urllib.parse import quote
import re

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "ebirime_connect.db"

st.set_page_config(page_title="Ebirime Connect", page_icon="🌱", layout="wide")

GREEN = "#14532D"
LIGHT_GREEN = "#DCFCE7"
CREAM = "#FAF7EF"

st.markdown(f"""
<style>
.stApp {{ background: {CREAM}; }}
[data-testid="stHeader"] {{ background: rgba(250,247,239,0.9); }}
h1,h2,h3 {{ color: {GREEN}; }}
div.stButton > button[kind="primary"] {{ background: {GREEN}; border-color: {GREEN}; color: white; }}
.ec-card {{ background: white; border: 1px solid #e5e7eb; border-radius: 16px; padding: 14px; margin-bottom: 10px; }}
.ec-price {{ color: {GREEN}; font-size: 1.1rem; font-weight: 700; }}
.ec-muted {{ color: #64748b; font-size: 0.9rem; }}
</style>
""", unsafe_allow_html=True)

def connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_name TEXT NOT NULL,
            seller_phone TEXT DEFAULT '',
            crop TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            price REAL NOT NULL,
            price_unit TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT DEFAULT '',
            photo_url TEXT DEFAULT '',
            available_from TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Available',
            created_at TEXT NOT NULL
        )
        """)
        count = con.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        if count == 0:
            samples = [
                ("Demo Farmer A", "", "Maize", 300, "kg", 1200, "per kg", "Masindi", "Dry maize, suitable for milling.", "", "Available now", "Available", "2026-10-12"),
                ("Demo Farmer B", "", "Beans", 90, "kg", 3800, "per kg", "Kabale", "Clean red beans.", "", "Available now", "Available", "2026-10-11"),
                ("Demo Farmer C", "", "Tomatoes", 800, "kg", 2500, "per kg", "Mbarara", "Fresh tomatoes. Please confirm availability.", "", "Available now", "Available", "2026-10-12"),
                ("Demo Farmer D", "", "Onions", 500, "kg", 3000, "per kg", "Wakiso", "Red onions.", "", "Available now", "Available", "2026-10-10"),
                ("Demo Farmer E", "", "Cassava", 40, "sacks", 40000, "per sack", "Gulu", "Fresh cassava roots.", "", "Available now", "Available", "2026-10-09"),
                ("Demo Farmer F", "", "Matooke", 50, "bunches", 15000, "per bunch", "Mbarara", "Green matooke bunches.", "", "Available now", "Available", "2026-10-12"),
                ("Demo Farmer G", "", "Potatoes", 200, "kg", 2200, "per kg", "Kisoro", "Irish potatoes.", "", "Available now", "Available", "2026-10-08"),
                ("Demo Farmer H", "", "Rice", 100, "kg", 4200, "per kg", "Bugiri", "Dry rice.", "", "Available now", "Available", "2026-10-07"),
            ]
            con.executemany("""
                INSERT INTO listings
                (seller_name,seller_phone,crop,quantity,unit,price,price_unit,location,description,photo_url,available_from,status,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, samples)

init_db()

if "role" not in st.session_state:
    st.session_state.role = "Buyer"
if "seller_name" not in st.session_state:
    st.session_state.seller_name = "Demo Farmer"
if "seller_phone" not in st.session_state:
    st.session_state.seller_phone = ""
if "selected_listing" not in st.session_state:
    st.session_state.selected_listing = None

with st.sidebar:
    st.markdown("## 🌱 Ebirime Connect")
    st.caption("Farmers meet buyers. Produce finds a market.")
    role = st.radio("I am using the app as", ["Buyer", "Farmer"], index=0 if st.session_state.role == "Buyer" else 1)
    st.session_state.role = role
    st.divider()
    page = st.radio("Navigate", ["Home", "Explore Produce", "Add Produce", "My Listings", "Profile"])
    st.divider()
    st.caption("MVP demo. Sample listings are fictional and prices are illustrative.")

st.title("🌱 Ebirime Connect")
st.caption("A simple marketplace connecting Ugandan farmers with produce buyers.")

def get_listings(available_only=False, seller=None):
    query = "SELECT * FROM listings"
    clauses, params = [], []
    if available_only:
        clauses.append("status = 'Available'")
    if seller:
        clauses.append("seller_name = ?")
        params.append(seller)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id DESC"
    with connect() as con:
        return con.execute(query, params).fetchall()

def format_ugx(value):
    return "UGX " + f"{value:,.0f}"


def listing_card(row):
    st.markdown('<div class="ec-card">', unsafe_allow_html=True)
    cols = st.columns([1, 3, 1])

    crop_photos = {
        "Maize": "https://share.google/EOCQ8CatKhrtfrrjh",
        "Beans": "https://images.unsplash.com/photo-1515543904379-3d757afe72e4?w=800",
        "Tomatoes": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=800",
        "Onions": "https://images.unsplash.com/photo-1508747703725-719777637510?w=800",
        "Cassava": "https://images.unsplash.com/photo-1596097635121-14b63b7a0c19?w=800",
        "Matooke": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=800",
        "Potatoes": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=800",
        "Rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800",
    }

    with cols[0]:
        crop_name = str(row["crop"]).strip()
        photo_url = str(row["photo_url"] or "").strip()
        image_url = photo_url or crop_photos.get(crop_name)

        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.write("Photo not available")

    with cols[1]:
        st.subheader(row["crop"])
        st.markdown(
            f"<div class='ec-price'>{format_ugx(row['price'])} {row['price_unit']}</div>",
            unsafe_allow_html=True,
        )
        st.write(f"**Quantity:** {row['quantity']:,.2f} {row['unit']}")
        st.write(f"📍 {row['location']} · {row['status']}")
        st.caption(f"Seller: {row['seller_name']} · Listed: {row['created_at']}")

    with cols[2]:
        if st.button("View details", key=f"view_{row['id']}", use_container_width=True):
            st.session_state.selected_listing = row["id"]
            st.session_state.page_override = "Listing Details"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# Allow navigation to a detail page from any listing.
if st.session_state.get("page_override") == "Listing Details":
    page = "Listing Details"
    st.session_state.page_override = None

if page == "Home":
    st.header("Good food. Stronger farmers. A brighter Uganda.")
    st.write("Find produce from Ugandan farmers, or publish what you have available.")
    search = st.text_input("🔎 What produce are you looking for?", placeholder="Try maize, beans or tomatoes")
    cats = ["All", "Maize", "Beans", "Tomatoes", "Onions", "Cassava", "Matooke", "Potatoes", "Rice"]
    chosen = st.selectbox("Browse a crop category", cats)
    rows = get_listings(available_only=True)
    if search:
        rows = [r for r in rows if search.lower() in r["crop"].lower() or search.lower() in r["location"].lower()]
    if chosen != "All":
        rows = [r for r in rows if r["crop"] == chosen]
    st.subheader("Freshly listed produce")
    if rows:
        for row in rows[:8]:
            listing_card(row)
    else:
        st.info("No matching produce found. Try another crop or location.")
    if st.session_state.role == "Farmer":
        st.info("Ready to sell? Choose **Add Produce** from the navigation menu.")

elif page == "Explore Produce":
    st.header("Explore Produce")
    c1, c2, c3 = st.columns(3)
    with c1:
        search = st.text_input("Search crop")
    with c2:
        location = st.text_input("Location contains")
    with c3:
        crop = st.selectbox("Crop", ["All", "Maize", "Beans", "Tomatoes", "Onions", "Cassava", "Matooke", "Potatoes", "Rice"])
    c4, c5 = st.columns(2)
    with c4:
        max_price = st.number_input("Maximum price (UGX per listed price unit)", min_value=0, value=0, step=500)
    with c5:
        sort = st.selectbox("Sort by", ["Newest", "Lowest price"])
    rows = get_listings(available_only=True)
    if search:
        rows = [r for r in rows if search.lower() in r["crop"].lower()]
    if location:
        rows = [r for r in rows if location.lower() in r["location"].lower()]
    if crop != "All":
        rows = [r for r in rows if r["crop"] == crop]
    if max_price > 0:
        rows = [r for r in rows if r["price"] <= max_price]
    if sort == "Lowest price":
        rows = sorted(rows, key=lambda r: r["price"])
    if rows:
        for row in rows:
            listing_card(row)
    else:
        st.info("No produce matches those filters.")

elif page == "Add Produce":
    st.header("Add Your Produce")
    if st.session_state.role != "Farmer":
        st.warning("Switch your role to Farmer in the sidebar to publish produce.")
    else:
        with st.form("add_listing", clear_on_submit=True):
            seller = st.text_input("Farmer or seller name", value=st.session_state.seller_name)
            phone = st.text_input("Phone number (optional for local demo)", value=st.session_state.seller_phone, placeholder="e.g. 2567XXXXXXXX")
            crop = st.selectbox("Crop", ["Maize", "Beans", "Tomatoes", "Onions", "Cassava", "Matooke", "Potatoes", "Rice", "Other"])
            if crop == "Other":
                crop = st.text_input("Enter crop name")
            c1, c2 = st.columns(2)
            with c1:
                quantity = st.number_input("Quantity available", min_value=0.0, value=0.0, step=1.0)
                unit = st.selectbox("Quantity unit", ["kg", "tonnes", "bags", "sacks", "bunches", "crates"])
            with c2:
                price = st.number_input("Asking price (UGX)", min_value=0.0, value=0.0, step=500.0)
                price_unit = st.selectbox("Price is", ["per kg", "per tonne", "per bag", "per sack", "per bunch", "per crate", "for all"])
            location = st.text_input("District, town or market", placeholder="e.g. Gulu, Mbarara, Wakiso")
            available_from = st.text_input("Availability", value="Available now", placeholder="e.g. Available now or from 20 Oct")
            photo_url = st.text_input("Photo URL (optional)", placeholder="A publicly accessible image URL")
            description = st.text_area("Description (optional)", placeholder="Describe the produce, quality or collection details.")
            submitted = st.form_submit_button("Publish Listing", type="primary", use_container_width=True)
        if submitted:
            if not seller.strip() or not crop.strip() or not location.strip():
                st.error("Please enter seller name, crop and location.")
            elif quantity <= 0 or price <= 0:
                st.error("Quantity and price must be greater than zero.")
            else:
                today = date.today().isoformat()
                with connect() as con:
                    con.execute("""
                    INSERT INTO listings (seller_name,seller_phone,crop,quantity,unit,price,price_unit,location,description,photo_url,available_from,status,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (seller.strip(), phone.strip(), crop.strip(), quantity, unit, price, price_unit, location.strip(), description.strip(), photo_url.strip(), available_from.strip(), "Available", today))
                st.session_state.seller_name = seller.strip()
                st.session_state.seller_phone = phone.strip()
                st.success("Listing published and saved on this device!")
                st.rerun()

elif page == "My Listings":
    st.header("My Listings")
    if st.session_state.role != "Farmer":
        st.warning("Switch your role to Farmer in the sidebar to manage listings.")
    else:
        name = st.text_input("Your seller name (must match your listing)", value=st.session_state.seller_name)
        rows = get_listings(seller=name.strip())
        if not rows:
            st.info("No listings found for this seller name. Add a listing first, using the same name.")
        for row in rows:
            with st.expander(f"{row['crop']} — {format_ugx(row['price'])} {row['price_unit']} · {row['status']}"):
                with st.form(f"edit_{row['id']}"):
                    new_qty = st.number_input("Quantity", min_value=0.0, value=float(row["quantity"]), key=f"qty_{row['id']}")
                    new_price = st.number_input("Price (UGX)", min_value=0.0, value=float(row["price"]), key=f"price_{row['id']}")
                    new_location = st.text_input("Location", value=row["location"], key=f"loc_{row['id']}")
                    new_status = st.selectbox("Status", ["Available", "Sold"], index=0 if row["status"] == "Available" else 1, key=f"status_{row['id']}")
                    save = st.form_submit_button("Save changes")
                if save:
                    if new_qty <= 0 or new_price <= 0 or not new_location.strip():
                        st.error("Quantity, price and location must be valid.")
                    else:
                        with connect() as con:
                            con.execute("UPDATE listings SET quantity=?,price=?,location=?,status=? WHERE id=?", (new_qty, new_price, new_location.strip(), new_status, row["id"]))
                        st.success("Listing updated.")
                        st.rerun()
                if st.button("Delete listing", key=f"delete_{row['id']}"):
                    st.session_state[f"confirm_delete_{row['id']}"] = True
                if st.session_state.get(f"confirm_delete_{row['id']}", False):
                    st.warning("Are you sure you want to delete this listing?")
                    yes, no = st.columns(2)
                    with yes:
                        if st.button("Yes, delete", key=f"yesdel_{row['id']}"):
                            with connect() as con:
                                con.execute("DELETE FROM listings WHERE id=?", (row["id"],))
                            st.session_state[f"confirm_delete_{row['id']}"] = False
                            st.success("Listing deleted.")
                            st.rerun()
                    with no:
                        if st.button("Cancel", key=f"nodel_{row['id']}"):
                            st.session_state[f"confirm_delete_{row['id']}"] = False
                            st.rerun()

elif page == "Profile":
    st.header("Profile")
    st.write("Use demo mode to explore the app without registering.")
    st.text_input("Display name", key="seller_name")
    st.text_input("Phone number (optional)", key="seller_phone")
    st.selectbox("Role", ["Buyer", "Farmer"], key="role")
    st.info("This MVP stores listings locally on the computer running the app. It does not yet share listings across users or devices.")
    st.caption("Ebirime Connect — Farmers meet buyers. Produce finds a market.")

elif page == "Listing Details":
    listing_id = st.session_state.get("selected_listing")
    with connect() as con:
        row = con.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
    if not row:
        st.error("This listing could not be found.")
    else:
        if st.button("← Back to Home"):
            st.session_state.selected_listing = None
            st.rerun()
        st.header(row["crop"])
        if row["photo_url"]:
            st.image(row["photo_url"], use_container_width=True)
        st.subheader(f"{format_ugx(row['price'])} {row['price_unit']}")
        st.write(f"**Quantity available:** {row['quantity']:,.2f} {row['unit']}")
        st.write(f"**Location:** {row['location']}")
        st.write(f"**Status:** {row['status']}")
        st.write(f"**Seller:** {row['seller_name']}")
        st.write(f"**Description:** {row['description'] or 'No description provided.'}")
        st.caption(f"Listed on {row['created_at']} · Availability: {row['available_from']}")
        phone = re.sub(r"[^0-9+]", "", row["seller_phone"] or "")
        if phone:
            msg = quote(f"Hello, I found your {row['crop']} listing on Ebirime Connect. Is it still available?")
            wa_phone = phone.replace("+", "")
            a, b = st.columns(2)
            with a:
                st.link_button("📞 Call Farmer", f"tel:{phone}", use_container_width=True)
            with b:
                st.link_button("💬 WhatsApp Farmer", f"https://wa.me/{wa_phone}?text={msg}", use_container_width=True)
        else:
            st.info("This is a demo listing with no contact number configured. Contact buttons become available when a valid number is added.")
        st.warning("Demo marketplace: verify the seller, price, quantity and quality before making any transaction.")

st.divider()
st.caption("Ebirime Connect MVP · Prototype for testing. Sample listings are illustrative, not live market offers.")
