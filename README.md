# Qatar Foundation Admin Portal — Sky Foundation

> Tech Stack: Python · Flask · SQLite · HTML · CSS · JavaScript

---

## 📖 Overview

This project is the **backend implementation** for the Qatar Foundation (Sky Foundation) Admin Portal. The complete Admin UI was provided as part of the assessment repository. The task was to build only the backend using **Python and Flask**, wiring it to the existing frontend without modifying any UI design, layout, or components.

---

## ✅ User Stories Implemented

### Task 1 — Login & Signup


| Feature | Description |
|---------|-------------|
| Admin Sign Up | Admins create accounts with full name, email, password, and confirm password. All fields are validated — duplicate emails are rejected, passwords must be ≥ 8 characters and match. |
| Admin Login | Login via email and password with a generic error message. Supports **Remember Me** (30-day session). On success, loads the admin's dashboard. |
| Forgot Password | Always shows the same success message for privacy. For registered emails, generates a secure reset token, logs the link internally, and enforces a **1-hour expiry**. |

### Task 2 — Opportunity Management


| Feature | Description |
|---------|-------------|
| View All Opportunities | Loads all opportunities belonging to the logged-in admin from the database. Shows name, category, duration, start date, and description. Displays an empty state when none exist. |
| Add a New Opportunity | Modal form with required fields (name, duration, start date, description, skills, category, future opportunities) and an optional max applicants field. On submit, saves to DB and renders the card instantly — no page refresh. |
| Opportunities Persist After Login | All opportunities are stored in SQLite and fetched fresh on each login. Admins only ever see their own data. |
| View Opportunity Details | Each card has a View button that opens a modal showing all saved fields including skills and future opportunities. |
| Edit an Opportunity | Edit button opens the same form modal pre-filled with existing data. On submit, updates the record via `PUT /api/opportunities/:id` and refreshes the card immediately. |
| Delete an Opportunity | Delete button shows a confirmation prompt. On confirm, permanently removes the record via `DELETE /api/opportunities/:id`. Only the admin who created it can delete it — enforced at the backend. |

---

## 🗄️ Database

**Database Engine:** SQLite (file: `admin.db`)

SQLite was chosen for its zero-configuration setup, making it ideal for local development and assessment environments. No separate database server is required — the DB file is created automatically on first run.

### Tables

```
admin
├── id               String(36)   PRIMARY KEY   UUID v7
├── full_name        String(150)  NOT NULL
├── email            String(150)  UNIQUE NOT NULL
├── password_hash    String(256)  NOT NULL
└── created_at       DateTime

opportunity
├── id                   String(36)   PRIMARY KEY   UUID v7
├── admin_id             String(36)   FK → admin.id
├── name                 String(200)  NOT NULL
├── duration             String(100)  NOT NULL
├── start_date           String(50)   NOT NULL
├── description          Text         NOT NULL
├── skills               Text         NOT NULL
├── category             String(50)   NOT NULL
├── future_opportunities Text         NOT NULL
├── max_applicants       Integer      NULLABLE
└── created_at           DateTime

password_reset_token
├── id          String(36)   PRIMARY KEY   UUID v7
├── admin_id    String(36)   FK → admin.id
├── token       String(256)  UNIQUE NOT NULL
├── expires_at  DateTime     NOT NULL
└── used        Boolean      default False
```

### UUID v7

All primary keys use **UUID v7** — a time-ordered UUID format (RFC 9562). UUID v7 encodes the creation timestamp in the high bits, making IDs both globally unique and naturally sortable by time. Implemented inline without any extra dependencies.

---

## 🗂️ Project Structure

```
Test1/
├── run.py                        # Entry point: python run.py
├── requirements.txt              # Python dependencies
├── admin.db                      # SQLite database (auto-created)
├── reset_links.log               # Internal log for password reset links
│
├── backend/
│   ├── app.py                    # Flask app factory
│   ├── config.py                 # SECRET_KEY, DB URI, session config
│   ├── extensions.py             # SQLAlchemy + LoginManager instances
│   ├── models.py                 # Admin, Opportunity, PasswordResetToken
│   └── routes/
│       ├── auth.py               # /api/auth/* endpoints
│       └── opportunities.py      # /api/opportunities/* endpoints
│
└── sky/                          # Frontend (provided, not modified)
    ├── admin.html
    ├── admin.css
    └── admin.js
```

---

## 🔌 API Endpoints

### Auth — `/api/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/signup` | ❌ | Create admin account |
| POST | `/login` | ❌ | Login, start session |
| POST | `/logout` | ✅ | End session |
| GET  | `/me` | ❌ | Get current session user |
| POST | `/forgot-password` | ❌ | Generate reset link |

### Opportunities — `/api/opportunities`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | ✅ | Get all opportunities for logged-in admin |
| POST | `/` | ✅ | Create new opportunity |
| PUT | `/:id` | ✅ | Update opportunity (owner only) |
| DELETE | `/:id` | ✅ | Delete opportunity (owner only) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip

### Install & Run

```bash
# 1. Clone the repository
git clone https://github.com/Meghashree-V/CertifyMe-Assessment.git
cd CertifyMe-Assessment

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python run.py
```

Open your browser at: **http://127.0.0.1:5000**

The SQLite database (`admin.db`) is created automatically on first run.

---

## 📦 Dependencies

```
flask               Web framework
flask-sqlalchemy    ORM for SQLite
flask-login         Session-based authentication
flask-cors          CORS headers for API requests
werkzeug            Password hashing utilities
python-dotenv       .env file support
```

---

## 🔐 Security Notes

- Passwords are hashed using **Werkzeug's `generate_password_hash`** (PBKDF2-SHA256)
- Sessions are signed with a **SECRET_KEY**
- Password reset tokens are **cryptographically random** (`secrets.token_hex(32)`) and expire after 1 hour
- Opportunity endpoints enforce **ownership** — admins cannot edit or delete other admins' data
- Forgot password always returns the **same response** regardless of whether the email exists (prevents user enumeration)

---

## 📋 Notes

- The frontend (`sky/`) was provided as part of the assessment and **was not redesigned**
- Only `admin.js` was modified to wire the existing UI to the new API endpoints
- All opportunity data is loaded from the database — no hardcoded cards exist in the HTML
