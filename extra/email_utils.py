from email.header import decode_header
import imaplib
import email


class EmailUtils:
    @staticmethod
    def get_imap_server(email_address):
        """Returns the IMAP server based on the email domain."""
        if email_address.endswith('@rambler.ru'):
            return 'imap.rambler.ru'
        elif email_address.endswith('@gmail.com'):
            return 'imap.gmail.com'
        elif email_address.endswith('@mail.ru'):
            return 'imap.mail.ru'
        elif "@firstmail" in email_address:
            return 'imap.firstmail.ltd'
        else:
            raise ValueError('Unsupported email domain.')

    @staticmethod
    def get_verification_link(email_address, password) -> str:
        """Logs into the IMAP server and searches for emails from support@wynd.network."""
        try:
            imap_server = EmailUtils.get_imap_server(email_address)

            # Connect to the server
            mail = imaplib.IMAP4_SSL(imap_server)

            # Login to the account
            mail.login(email_address, password)
            mail.select('inbox')

            status, messages = mail.search(None, 'FROM', 'support@wynd.network')

            email_ids = messages[0].split()
            email_ids.reverse()  # Process the newest email first

            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')

                        # Print the body of the email
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get('Content-Disposition'))
                                if 'attachment' not in content_disposition:
                                    body = part.get_payload(decode=True)
                                    if body:
                                        body = body.decode()
                                        if "https://app.getgrass.io/confirm-email/?token" in body:
                                            return "https://app.getgrass.io/confirm-email/?token" + body.split("https://app.getgrass.io/confirm-email/?token")[1].split('"')[0]
                        else:
                            body = msg.get_payload(decode=True)
                            if body:
                                body = body.decode()
                                if "https://app.getgrass.io/confirm-email/?token" in body:
                                    return "https://app.getgrass.io/confirm-email/?token" + body.split("https://app.getgrass.io/confirm-email/?token")[1].split('"')[0]

            mail.logout()
            return ""
        except Exception as e:
            return ""
