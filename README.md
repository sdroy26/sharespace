# ShareSpace

**Good resources shouldn't sit idle.** ShareSpace is a Django campus resource-sharing MVP focused on safe access, transparent decisions, condition records, and auditable handovers.

## What is implemented

- Django authentication with a custom user model; registration always creates a borrower account.
- Resource directory with search, category/location filters, pagination, owner listing management, publication review, and availability windows.
- Booking request validation for future times, advance notice, duration, institution, training, active booking limits, allowed availability windows, duplicate requests, and overlap checks.
- Owner approval/rejection with mandatory rejection reasons and an availability recheck.
- FIFO-style waitlist promotion to pending owner review when a released slot is compatible.
- Check-in and return condition reports, optional image upload, supervised-return confirmation, incident reports, persisted notifications, and audit timeline.
- Borrower, owner, and institutional dashboards based on database records.
- Manager verification, incident review, user access controls, and read-only audit history.
- Responsive editorial UI, no remote font/icon dependencies, CSRF-protected state changes, development seed data, and overdue management command.

## Stack

Python 3.12+; Django 5.2; SQLite for local development; Django templates; HTML/CSS/vanilla JavaScript; Pillow; WhiteNoise; Gunicorn. The core app does not require any external API credentials.

## Prerequisites and local setup

Use Python 3.12 or newer. From the project directory:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
python manage.py makemigrations accounts resources bookings audit notifications
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000. If your platform does not support copying `.env.example`, create `.env` manually. The development fallback secret key is not suitable for production.

### Demo credentials

All demo accounts use password `ShareSpaceDemo!26`:

| Username | Role |
|---|---|
| `campusadmin` | Institution manager (staff access) |
| `maya_owner` | Resource owner |
| `arjun_owner` | Resource owner |
| `isha_borrower` | Borrower |
| `rohan_borrower` | Borrower |
| `nina_borrower` | Borrower |
| `dev_borrower` | Borrower |

The seed command is idempotent for named accounts, resources, and its representative records. It does not reset existing account passwords or delete application data. Do not use demo credentials in a public deployment.

## Tests and checks

```bash
python manage.py check
python manage.py test
python manage.py test accounts resources bookings operations core
```

Django's test runner discovers tests in the app `tests.py` files. `pytest` is also configured if you prefer `pytest`. Tests were authored but **could not be executed in the generation environment** because Django dependencies could not be downloaded there (network/DNS unavailable). Run the commands above in an environment with package access and fix any environment-specific issues before presenting this as production-ready.

## Judge walkthrough (3–5 minutes)

1. Sign in as `maya_owner` and open Owner overview / Managed resources.
2. Sign in as `isha_borrower`, find a published resource, inspect its Trust & readiness panel, and request a future slot.
3. Sign in as the relevant owner and review the request in Booking requests.
4. Return to the borrower and inspect the notification and booking detail.
5. For a lifecycle demo, use a fresh approved booking whose start is within the allowed check-in window, submit the check-in condition report, then record return condition.
6. Show the timeline and condition comparison. Submit an issue to demonstrate incident review.

Seed data includes sample booking states and records for dashboard density; not every sample booking is positioned at a time that permits a live check-in. For a live walkthrough, create a new booking starting 10–20 minutes in the future, approve it, and check it in during that window. For resources with a configured availability window, select a time wholly inside that window.

## Architecture

- `accounts`: custom user model, safe registration, profile editing.
- `resources`: resource metadata, availability windows, eligibility records, discovery, owner listing workflows.
- `bookings`: booking, condition report, incident models; forms; booking service transitions.
- `notifications`: persisted recipient-scoped in-app notifications and read actions.
- `audit`: append-only event model and trusted service helper.
- `operations`: institutional review, user access, incident management, audit views.
- `core`: public pages and role-based dashboards.

Important transitions are implemented in `bookings/services.py`; views call those functions rather than accepting arbitrary status values. The audit log is not editable through normal views and is read-only in Django admin. A platform superuser can still alter the database directly, as is inherent in an application administrator role.

## Fairness and allocation policy

- Eligibility and safety checks take precedence over access.
- Valid requests are owner-reviewed; requests are not automatically approved.
- Conflicting valid requests can be waitlisted in creation-time order. A freed slot promotes the earliest compatible waitlisted request to **pending owner review**, not directly to approved.
- Approved borrowers are not silently displaced.
- Rejections require a reason; the competing borrower's identity is not exposed.
- Active booking limits are enforced per resource/user workflow. No AI model assigns priority or liability.

## Database and concurrency notes

SQLite is convenient for local demos but does not provide the same row-locking semantics as PostgreSQL. The service layer uses `transaction.atomic()` and `select_for_update()` for transition consistency; on SQLite, row-level locking is not equivalent to PostgreSQL. For production, configure PostgreSQL and add a PostgreSQL exclusion constraint over a timestamp range to prevent overlapping active reservations at the database level. The current code performs application-level overlap checks; simultaneous conflicting approvals should be load-tested against the intended production database.

Availability is modeled as explicit windows. If a resource has one or more windows, a requested booking must fit fully inside one window. If no windows exist, availability is governed by resource status, advance notice, duration, and active bookings. Recurring weekly schedules are not implemented in this MVP.

## Production deployment

1. Install dependencies and use a persistent PostgreSQL database. Do not use SQLite on ephemeral deployment storage for multi-user production.
2. Set environment variables: `SECRET_KEY` to a strong random value, `DEBUG=False`, `ALLOWED_HOSTS=your-host.example`, and `SECURE_SSL_REDIRECT=True` when HTTPS is correctly configured. Add `CSRF_TRUSTED_ORIGINS=https://your-host.example` to settings if cross-origin HTTPS POSTs require it (the current settings file should be extended to parse this variable before deployment).
3. Set `DATABASE_URL` to a PostgreSQL connection URL (and `DB_SSLMODE=require` for a managed TLS database). The settings parse PostgreSQL URLs and retain SQLite when `DATABASE_URL` is blank. Do not commit credentials.
4. Run `python manage.py makemigrations` as needed, `python manage.py migrate`, `python manage.py collectstatic`, and create a real superuser. Do not run `seed_demo` in production.
5. Start with `gunicorn config.wsgi:application`. The included `Procfile` provides this command for compatible platforms.
6. WhiteNoise serves collected static assets. Uploaded media is stored on the local filesystem by default; many free hosting filesystems are ephemeral. Use a persistent media volume or private object storage for uploaded images, and configure access controls/retention before production.
7. Run `python manage.py check --deploy`, review HTTPS/cookie settings, configure backups and retention, and test restore procedures.

Free hosting tiers, persistent storage, database quotas, and usage limits change frequently. Confirm current provider terms rather than assuming a free tier is permanent. No deployment is included or claimed by this source delivery.

## Security and privacy notes

- Django password hashing, CSRF middleware, ORM queries, template escaping, POST state changes, role/object checks, and upload size/type checks are used.
- Registration cannot self-assign owner/manager roles. Institutional role assignment is manager-only; platform administration remains separate via Django superuser.
- Verification evidence is represented by reviewed statuses rather than identity-document uploads. Do not upload sensitive documents or unrelated personal information.
- Condition and incident images are stored under separate media paths, but the default development media serving is not a private-media access-control solution. Before production, use authenticated media views or private object storage for sensitive uploads.
- Basic login rate limiting is not bundled. Add trusted proxy-aware rate limiting at the reverse proxy or a reviewed Django package before public exposure.
- Configure data retention, deletion requests, institutional privacy policies, backups, and incident response before production.

## External services and AI disclosure

No AI feature, paid API, map service, SMTP provider, or external authentication is required or called by the core application. Django's console email backend is configured by default. SMTP can be configured through environment variables in a deployment-specific settings extension. The interface uses local CSS and system fonts.

## Known limitations / next steps

- Add migrations generated and reviewed for the target Django version to version control before a formal release.
- Add PostgreSQL exclusion constraints and concurrency integration tests.
- Complete extension-request UI and decision workflow; the model includes extension fields but the full extension interface is not implemented.
- Add explicit owner return-confirmation UI on the booking detail (the service and POST endpoint exist).
- Add private media delivery, login rate limiting, and comprehensive upload content sniffing.
- Add recurring availability rules, automated reminders/scheduler, richer suitability scoring, and more extensive test coverage.
- Configure institutional policy for data retention and verification before real campus use.

## Team contributions

- Product / strategy: [Name]
- Backend / Django: [Name]
- Frontend / UX: [Name]
- QA / deployment: [Name]

## Licences

The project code is provided for hackathon use. Runtime dependencies are open-source; check the licence of each pinned dependency and retain applicable notices when redistributing. No third-party fonts, icons, or image APIs are bundled.
