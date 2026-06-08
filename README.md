# Email News Automation

A small Django app for storing newsletter recipients, importing recipient CSV files, fetching topic-based news with NewsAPI, and sending a clean HTML digest through SMTP.

## Features

- SQLite-backed recipient storage with Django models
- Manual recipient add, delete, and list screens
- CSV import with `name,email` headers
- Duplicate email prevention and email validation
- Separate campaign screen for previewing and sending a topic digest
- Top 5 NewsAPI articles per topic, selected from a larger locally ranked candidate pool
- HTML email formatting
- Basic campaign history and per-recipient delivery status
- Django admin support for recipients, campaigns, and deliveries

## Project Structure

```text
email_news_automation/
  email_news_automation/
    settings.py
    urls.py
    wsgi.py
  newsletter/
    models.py                 # Recipient, Campaign, Delivery
    forms.py                  # Recipient, CSV, and campaign forms
    views.py                  # Recipient management and campaign UI
    urls.py
    services/
      campaigns.py            # Preview/send workflow
      email_formatting.py     # HTML digest builder
      email_sender.py         # SMTP delivery
      news.py                 # NewsAPI integration
      recipients.py           # CSV import helpers
    templates/newsletter/
    static/newsletter/
    migrations/
  manage.py
  main.py
  requirements.txt
  README.md
```

## Environment Variables

Create a `.env` file in the project root:

```env
EMAIL=your_email@gmail.com
PASSWORD=your_gmail_app_password
API_KEY=your_newsapi_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
DJANGO_SECRET_KEY=change-this-for-production
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

`SMTP_HOST`, `SMTP_PORT`, and the Django settings are optional for local development. Gmail users should use an App Password.

## Run Locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

The SQLite database is created automatically as `newsletter.db` when migrations run.

## CSV Import Format

Upload a UTF-8 CSV file with this header:

```csv
name,email
Sahil,sahil@example.com
Alex,alex@example.com
```

Malformed rows are rejected. Duplicate emails already in the database or repeated inside the same file are skipped.

## Usage

1. Add recipients manually or import a CSV on the Recipients page.
2. Go to Campaigns.
3. Enter a topic.
4. Preview the generated digest.
5. Send the digest to all stored recipients.

## Notes

- Keep `.env` private. It should not be committed.
- Free NewsAPI accounts have request limits and may restrict article age.
- Delivery failures are recorded per recipient so a campaign can finish even if one address fails.
