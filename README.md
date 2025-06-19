# nagios-check-email-round-trip

Nagios plugin to monitor the email round trip status. It will create and send an
email message to an email address, and check an IMAP mailbox for the message to
arrive. Possible states:

* `OK` when the message arrives within 10 minutes in the `INBOX`
* `WARNING` when the message arives within 10 minutes in the `Spam` folder
* `CRITICAL` when the message does not arrive within 10 minutes


# Requirements

* Python 3.6 or newer
* An SMTP relay server to send mail through
* An IMAP account that will receive the message


# Usage

```
usage: check-email-round-trip.py [-h] --smtp-server SMTP_SERVER [--smtp-port SMTP_PORT]
                                 [--smtp-username SMTP_USERNAME] [--smtp-password SMTP_PASSWORD]
                                 --smtp-from SMTP_FROM --smtp-to SMTP_TO [--subject-prefix SUBJECT_PREFIX]
                                 [--smtp-debuglevel SMTP_DEBUGLEVEL] --imap-server IMAP_SERVER
                                 [--imap-port IMAP_PORT] --imap-username IMAP_USERNAME --imap-password IMAP_PASSWORD
                                 [--imap-inbox-folder IMAP_INBOX_FOLDER] [--imap-spam-folder IMAP_SPAM_FOLDER]
                                 [--imap-poll-interval IMAP_POLL_INTERVAL] [--max-wait MAX_WAIT] [-v]

A Nagios script to monitor an email round trip

options:
  -h, --help            show this help message and exit
  --smtp-server SMTP_SERVER
                        SMTP server address (default: None)
  --smtp-port SMTP_PORT
                        SMTP server port (default: 587)
  --smtp-username SMTP_USERNAME
                        SMTP username (default: None)
  --smtp-password SMTP_PASSWORD
                        SMTP password (default: None)
  --smtp-from SMTP_FROM
                        FROM address to use for sending (default: None)
  --smtp-to SMTP_TO     TO address to use for sending (default: None)
  --subject-prefix SUBJECT_PREFIX
                        Optional prefix for the message's Subject header. (default: Email monitoring )
  --smtp-debuglevel SMTP_DEBUGLEVEL
                        SMTP debug level (default: 0)
  --imap-server IMAP_SERVER
                        IMAP server address (default: None)
  --imap-port IMAP_PORT
                        IMAP server port (default: 993)
  --imap-username IMAP_USERNAME
                        IMAP username (default: None)
  --imap-password IMAP_PASSWORD
                        IMAP password (default: None)
  --imap-inbox-folder IMAP_INBOX_FOLDER
                        IMAP INBOX folder (default: INBOX)
  --imap-spam-folder IMAP_SPAM_FOLDER
                        IMAP Spam folder (default: Spam)
  --imap-poll-interval IMAP_POLL_INTERVAL
                        IMAP polling interval (seconds) (default: 5)
  --max-wait MAX_WAIT   Maximum time (seconds) to wait for message (default: 600)
  -v, --verbosity       increase output verbosity (default: None)
```

# Caveats

* If you use a GMail IMAP account, the Spam folder name should be configured
  like this, including the double quotes:

  ```
  --imap-spam-folder '"[Gmail]/Spam"'
  ```

# To do

* Allow reading credentials from files instead of command line arguments