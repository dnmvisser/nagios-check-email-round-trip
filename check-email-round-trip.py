#!/usr/bin/env python3
import argparse
import datetime
import imaplib
import smtplib
import sys
import time
import uuid
from email.message import EmailMessage
from email.utils import make_msgid

ap = argparse.ArgumentParser(
    description="A Nagios script to monitor an email round trip",
    # epilog="BUGS: no known bugs",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

# Arg names with dashes will become variables with underscores
ap.add_argument("--smtp-server", help="SMTP server address", required=True)
ap.add_argument("--smtp-port", help="SMTP server port", default=587)
ap.add_argument("--smtp-username", help="SMTP username")
ap.add_argument("--smtp-password", help="SMTP password")
ap.add_argument("--smtp-from", help="FROM address to use for sending", required=True)
ap.add_argument("--smtp-to", help="TO address to use for sending", required=True)
ap.add_argument(
    "--subject-prefix",
    help="Optional prefix for the message's Subject header.",
    default="Email monitoring ",
)
ap.add_argument("--smtp-debuglevel", help="SMTP debug level", default=0)
ap.add_argument("--imap-server", help="IMAP server address", required=True)
ap.add_argument("--imap-port", help="IMAP server port", default=993)
ap.add_argument("--imap-username", help="IMAP username", required=True)
ap.add_argument("--imap-password", help="IMAP password", required=True)
ap.add_argument("--imap-inbox-folder", help="IMAP INBOX folder", default="INBOX")
ap.add_argument("--imap-spam-folder", help="IMAP Spam folder", default="Spam")
ap.add_argument(
    "--imap-poll-interval", help="IMAP polling interval (seconds)", default=5
)
ap.add_argument(
    "--max-wait", help="Maximum time (seconds) to wait for message", default=600
)
ap.add_argument("-v", "--verbosity", action="count", help="increase output verbosity")
args = ap.parse_args()

SMTP_SERVER = args.smtp_server
SMTP_PORT = args.smtp_port
SMTP_USERNAME = args.smtp_username
SMTP_PASSWORD = args.smtp_password
FROM_EMAIL = args.smtp_from
TO_EMAIL = args.smtp_to
SUBJECT = args.subject_prefix + str(uuid.uuid4())
SMTP_DEBUGLEVEL = args.smtp_debuglevel

IMAP_SERVER = args.imap_server
IMAP_PORT = args.imap_port
IMAP_USERNAME = args.imap_username
IMAP_PASSWORD = args.imap_password
IMAP_FOLDER_INBOX = args.imap_inbox_folder
IMAP_FOLDER_SPAM = args.imap_spam_folder
POLL_INTERVAL = int(args.imap_poll_interval)
MAX_WAIT_SECONDS = int(args.max_wait)
VERBOSITY = args.verbosity

# TODO find a way to override this with an argument
BODY = (
    f"This message is to test the delivery of email to {TO_EMAIL}, from "
    + f"{FROM_EMAIL}. It can be safely ignored."
)


def send_email():
    try:
        msg = EmailMessage()
        msg["Message-ID"] = make_msgid()
        msg["Subject"] = SUBJECT
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg.set_content(BODY)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(SMTP_DEBUGLEVEL)
            server.starttls()
            if None not in (SMTP_USERNAME, SMTP_PASSWORD):
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.mail(FROM_EMAIL)
            server.rcpt(TO_EMAIL)
            # sendmail() or send_message() does not return code/response,
            # so we resort to data()
            response_code, response_string = server.data(msg.as_string())
            server.quit()
            return response_code, response_string.decode()
    except Exception as e:
        print(f"UNKNOWN - an error occurred: {e}")
        sys.exit(3)


def check_imap_message(folders):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        # mail.debug = 4
        for _ in range(0, MAX_WAIT_SECONDS, POLL_INTERVAL):
            for folder in folders:
                if VERBOSITY is not None:
                    print(f"Checking for message in folder {folder}")
                mail.select(folder)
                result, data = mail.search(
                    None, f'(SUBJECT "{SUBJECT}" HEADER FROM "{FROM_EMAIL}")'
                )
                if result == "OK":
                    email_ids = data[0].split()
                    for email_id in email_ids:
                        result, msg_data = mail.fetch(email_id, "(RFC822)")
                        if result == "OK":
                            if VERBOSITY is not None:
                                print(f"Found message in folder {folder}")
                            # A tuple of the message, and the folder it was in
                            return msg_data[0][1].decode(), folder
            time.sleep(POLL_INTERVAL)
        return None, None
    except Exception as e:
        print(f"UNKNOWN - an error occurred: {e}")
        sys.exit(3)


def main():
    try:
        smtp_code, smtp_response = send_email()
        sent_at = datetime.datetime.now()
        smtp_log = (
            f"SMTP server {SMTP_SERVER}:{SMTP_PORT} said: {smtp_code} {smtp_response}"
        )
    except Exception as e:
        print(f"CRITICAL - Failed to send email: {e}")
        sys.exit(2)

    # Try to fetch the message
    found_message, folder = check_imap_message([IMAP_FOLDER_INBOX, IMAP_FOLDER_SPAM])

    if found_message is not None:
        received_at = datetime.datetime.now()
        round_trip_time = round((received_at - sent_at).total_seconds())
        imap_log = f"IMAP server {IMAP_SERVER}:{IMAP_PORT} contains message in {folder}:\n\n{found_message}"
        perf_data = f"rtt={round_trip_time}"
        result = f"Email arrived in {folder}, message round trip took {round_trip_time} seconds | {perf_data}\n{smtp_log}\n{imap_log}"

        if folder == IMAP_FOLDER_INBOX:
            print(f"OK - {result}")
            sys.exit(0)
        if folder == IMAP_FOLDER_SPAM:
            print(f"WARNING - {result}")
            sys.exit(1)
    else:
        print(
            f"CRITICAL - Email message not received within timeout of {MAX_WAIT_SECONDS} seconds\n{smtp_log}"
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
