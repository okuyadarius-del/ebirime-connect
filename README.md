# Ebirime Connect MVP

A beginner-friendly Python + Streamlit prototype for a Ugandan produce marketplace.

## Run on Windows

1. Install Python if needed.
2. Open Command Prompt in this folder.
3. Install requirements:

   `python -m pip install -r requirements.txt`

4. Start the app:

   `python -m streamlit run app.py`

5. Your browser should open at `http://localhost:8501`.

## What works

- Home and produce browsing
- Search, crop and location filters
- Add listings
- Edit listing quantity, price and location
- Mark listings available or sold
- Delete listings
- Listing details and contact links when a real phone number is configured
- SQLite local database persistence on the computer running the app

## Important limitations

This is a local prototype. The SQLite database is stored on the computer running the app. It does not sync listings across different users or phones. Do not enter sensitive personal information. Sample listings are fictional and prices are illustrative.

For a public multi-user launch, connect a hosted database and authentication, then deploy using a hosting service. Streamlit Community Cloud can host a prototype from GitHub, but persistent shared storage should be configured separately.
