import argparse
import os
import sys
import logging
from email.message import EmailMessage
import smtplib

import pandas as pd
from jinja2 import Template
from dotenv import load_dotenv


def load_contacts(path, sheet_name=None):
    if path.lower().endswith('.csv'):
        return pd.read_csv(path)
    else:
        return pd.read_excel(path, sheet_name=sheet_name)


def render_message(template_text, context):
    tpl = Template(template_text)
    return tpl.render(**context)


def send_smtp_message(smtp_host, smtp_port, smtp_user, smtp_pass, use_ssl, msg):
    if use_ssl:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
    else:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
    server.quit()


def main():
    parser = argparse.ArgumentParser(description='Send personalized emails from an Excel/CSV file')
    parser.add_argument('input', help='Input file (.xlsx or .csv)')
    parser.add_argument('--sheet', help='Sheet name (for Excel files)', default=None)
    parser.add_argument('--template-file', help='Path to message template (Jinja2)', default=None)
    parser.add_argument('--subject', help='Email subject or column name', default='Hello from script')
    parser.add_argument('--email-col', help='Column name for recipient email', default='email')
    parser.add_argument('--name-col', help='Column name for recipient name', default='name')
    parser.add_argument('--from-name', help='Sender name (overrides .env FROM_NAME)', default=None)
    parser.add_argument('--dry-run', help='Do not actually send emails, just print', action='store_true')
    args = parser.parse_args()

    load_dotenv()
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASS = os.getenv('SMTP_PASS')
    FROM_EMAIL = os.getenv('FROM_EMAIL')
    FROM_NAME = os.getenv('FROM_NAME')
    SMTP_SSL = os.getenv('SMTP_SSL', 'false').lower() in ('1', 'true', 'yes')

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
        logging.error('Missing SMTP configuration in environment. Copy .env.example to .env and edit.')
        sys.exit(1)

    contacts = load_contacts(args.input, sheet_name=args.sheet)

    if args.template_file:
        with open(args.template_file, 'r', encoding='utf-8') as f:
            template_text = f.read()
    else:
        template_text = None

    for idx, row in contacts.iterrows():
        try:
            to_email = row[args.email_col]
        except KeyError:
            logging.error('Email column "%s" not found in input', args.email_col)
            sys.exit(1)

        context = row.to_dict()
        context['from_name'] = args.from_name or FROM_NAME

        if template_text:
            body = render_message(template_text, context)
        else:
            # Prefer a 'message' column if present, else a simple fallback
            body = row.get('message') if 'message' in row.index else f"Hello {row.get(args.name_col, '')},\n"

        subject = args.subject
        if subject in contacts.columns:
            subject = row[subject]

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = f"{context['from_name']} <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg.set_content(body)

        if args.dry_run:
            print('---')
            print(f'To: {to_email}')
            print(f'Subject: {subject}')
            print(body)
            continue

        send_smtp_message(SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_SSL, msg)
        print(f'Sent to {to_email}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
