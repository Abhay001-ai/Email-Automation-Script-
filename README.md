# Email Automation Script

Small Python utility to send personalized emails from an Excel or CSV file.

**Features**
- Read contacts from `.xlsx` or `.csv` (Pandas)
- Render personalized message using a Jinja2 template or a `message` column
- Send via SMTP (`smtplib`) with support for SSL/TLS
- Dry-run mode to preview emails without sending

**Files**
- `send_emails.py` - main script
- `requirements.txt` - Python dependencies
- `.env.example` - SMTP configuration example
- `template.txt` - sample Jinja2 template
- `sample_contacts.csv` - sample contacts file

Getting started

1. Create a Python venv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in SMTP values.

3. Prepare your contacts file (`.xlsx` or `.csv`) with at least an `email` column and optional `name`, `message`, and other fields.

4. Run a dry-run to preview messages:

```powershell
python send_emails.py sample_contacts.csv --template-file template.txt --subject "Welcome" --dry-run
```

5. When ready, remove `--dry-run` to actually send messages.

Notes
- The script uses Jinja2 for template rendering; include placeholders like `{{ name }}` or `{{ company }}` that map to column names in your sheet.
- If you're using an Excel file with multiple sheets, pass `--sheet SheetName`.
