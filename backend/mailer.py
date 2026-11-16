"""Tiny mail helper (US14).

Messages always go to an in-process outbox (useful for tests and local dev).
If SMTP_HOST is set in the environment the message is also sent over SMTP.
"""
import logging
import os
import smtplib
from email.message import EmailMessage

log = logging.getLogger(__name__)

OUTBOX = []


def send_email(to, subject, body):
    OUTBOX.append({"to": to, "subject": subject, "body": body})
    host = os.environ.get("SMTP_HOST")
    if not host:
        log.info("Email to %s (no SMTP configured): %s", to, subject)
        return
    msg = EmailMessage()
    msg["From"] = os.environ.get("SMTP_FROM", "no-reply@splitbill.local")
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, int(os.environ.get("SMTP_PORT", "25")), timeout=10) as smtp:
            if os.environ.get("SMTP_USER"):
                smtp.starttls()
                smtp.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASSWORD", ""))
            smtp.send_message(msg)
    except OSError:
        log.exception("Could not deliver email to %s", to)
