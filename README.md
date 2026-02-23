# DropCode 📲

DropCode is a temporary QR-based photo sharing web app that allows users to upload images from one device and instantly access them on another.

The app generates a unique code and QR code for each upload session, creating a temporary gallery where photos can be previewed and downloaded individually.

It is designed to be simple, fast, and mobile-first — no accounts, no cloud storage setup, no friction.

---

## Why I Built This

I built DropCode after realizing how inconvenient it is to receive a photo taken by someone else without exchanging personal information.

My phone’s camera quality isn’t great, so asking someone with a better phone to take a picture makes sense — but there’s usually no simple way to get that photo unless you share phone numbers, social media, or use ecosystem-specific features that may not be compatible.

I wanted a way to transfer photos instantly using only a code, with:

- No contact exchange
- No accounts
- No ecosystem limitations
- Optimized for mobile use

DropCode solves that problem through temporary QR-based sharing.

---

## Tech Stack

- Python
- Flask
- SQLAlchemy
- SQLite
- APScheduler
- HTML / CSS / JavaScript

---

## How to Run

1. Clone the repository:

```bash
git clone git@github.com:ubuch/dropcode.git
cd dropcode
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

> **Note:** Use `python app.py` instead of `flask run` because the background scheduler starts inside the main entry point.

---

## Next Step

The next planned step is deploying the project to the web so it can be accessed from anywhere.

Deployment is currently pending and will be implemented using a lightweight cloud hosting platform.
