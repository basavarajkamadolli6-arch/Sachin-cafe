# Sachin Cafe 3.0 — Django + AI + Razorpay

A beginner-friendly full-stack demo cafe project. Separate Django templates, CSS, JS, SQLite models, staff dashboard, customer authentication, session cart, order history, AI chatbot and optional Razorpay Checkout.

## Windows setup (CMD)

1. Extract ZIP to `C:\SachinCafe3`.
2. Open **Command Prompt**:

```bat
cd /d C:\SachinCafe3
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_menu
python manage.py createsuperuser
python manage.py runserver
```

If `py -3.12` is not available, try `py -3 -m venv .venv` with an installed supported Python version.

Visit http://127.0.0.1:8000/ ; menu: `/menu/`; staff: `/dashboard/`; Django admin: `/admin/`.

## Real AI chatbot

Open `.env` and set `OPENAI_API_KEY=your_key_here`. Restart Django. Uses OpenAI Chat Completions through the backend. Without the key, the site shows a **basic rule-based** assistant, not a real AI model. API usage may cost money. Never paste API keys into HTML/JS or commit `.env`.

## Razorpay payment

1. Register a Razorpay merchant account and obtain **test mode** Key ID and Secret (subject to Razorpay eligibility and verification).
2. Add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` to `.env` and restart.
3. At checkout choose Razorpay, confirm order, open **My Orders** and click **Pay online**.
4. Backend creates the Razorpay order and verifies the payment signature and fetched payment details before marking paid.
5. For production, add verified payment webhooks, capture/reconciliation, refund workflows, and payment state handling before going live. Do not use live payments until these are implemented and tested.

## What works and limitations

- SQLite stores products, users, orders and order items. The cart uses Django sessions.
- Staff can change order status at `/dashboard/`; Django admin can edit products and prices.
- Budget suggestions are algorithmic filters (not a trained ML model).
- Chatbot is a real external AI integration only when a valid API key is configured; otherwise fallback rules.
- The location is **a placeholder**: set `CAFE_ADDRESS` to the verified actual cafe address. The Google Maps button searches for it; no real-time location tracking.
- GST is an **illustrative fixed 5%** and should be checked for your actual products, registration, tax status and local regulations before commercial use.
- Images load from Unsplash and require internet access; replace with licensed product photos.
- No delivery service, inventory locking, coupons, refunds, production webhooks, or ML training is implemented.
- Before production: set `DJANGO_DEBUG=False`, a unique `DJANGO_SECRET_KEY`, HTTPS, secure cookie settings, proper `ALLOWED_HOSTS`, a production WSGI server, production DB/backups, and rate limits for chat/login/checkout.

## File layout

```
manage.py
requirements.txt
.env.example
config/ (settings, urls, wsgi)
cafe/ (models, views, admin, context, seed_menu)
templates/cafe/ (base, index, menu, cart, checkout, orders, dashboard)
templates/registration/ (login, register)
static/css/style.css
static/js/app.js
```

## Helpful commands

```bat
python manage.py check
python manage.py makemigrations cafe
python manage.py migrate
python manage.py seed_menu
python manage.py runserver
```
