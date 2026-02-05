import os
import pickle
import imaplib
import email
import datetime
from email.header import decode_header
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

EMAIL = "yadnitkk@gmail.com"
SCOPES = ["https://mail.google.com/"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"

def get_gmail_creds():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return creds

def fetch_todays_emails():
    """
    Returns: a list of dicts, each representing one email.
    """
    results = []
    try:
        creds = get_gmail_creds()
        auth_str = f"user={EMAIL}\x01auth=Bearer {creds.token}\x01\x01".encode()

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.authenticate("XOAUTH2", lambda resp: auth_str)
        mail.select("INBOX")

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        criteria = f'(SINCE {today.strftime("%d-%b-%Y")} BEFORE {tomorrow.strftime("%d-%b-%Y")})'

        status, data = mail.search(None, criteria)
        if status != "OK":
            return {"error": data}

        ids = data[0].split()

        for msg_id in ids:
            msg_typ, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, enc = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                try:
                    subject = subject.decode(enc or "utf-8")
                except:
                    subject = subject.decode("utf-8", errors="ignore")

            from_ = msg.get("From")

            # Get text body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                        try:
                            body += part.get_payload(decode=True).decode()
                        except:
                            body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
            else:
                body = msg.get_payload(decode=True).decode()

            results.append({
                "id": msg_id.decode(),
                "from": from_,
                "subject": subject,
                "body": body.strip(),
            })

        mail.logout()
        return results

    except Exception as e:
        return {"error": str(e)}
