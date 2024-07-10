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
        else:
            return 'imap.firstmail.ltd'

    @staticmethod
    def get_verification_link(email_address, password) -> str:
        """Logs into the IMAP server and searches for emails from support@wynd.network."""
        try:
            imap_server = EmailUtils.get_imap_server(email_address)

            # Connect to the server
            mail = imaplib.IMAP4_SSL(imap_server)

            # Login to the account
            mail.login(email_address, password)

            # Function to search for the email in a specific mailbox
            def search_in_mailbox(mailbox_name):

                status, _ = mail.select(mailbox_name)
                if status != 'OK':
                    print(f"Failed to select mailbox: {mailbox_name}")
                    return None

                status, messages = mail.search(None, 'FROM', 'support@wynd.network')
                if status != 'OK':
                    print(f"Failed to search in mailbox: {mailbox_name}")
                    return None

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
                return None

            verification_link = search_in_mailbox('inbox')
            if verification_link:
                return verification_link

            status, mailboxes = mail.list()
            if status == 'OK':
                for mailbox in mailboxes:
                    mailbox_name = mailbox.decode().split(' "/" ')[-1].strip('"')
                    if 'Spam' in mailbox_name or 'Junk' in mailbox_name or 'spam' in mailbox_name:
                        verification_link = search_in_mailbox(mailbox_name)
                        if verification_link:
                            return verification_link

            mail.logout()
            return ""
        except Exception as e:
            return ""

    @staticmethod
    def get_solana_address_verification_link(email_address, password) -> str:
        """Logs into the IMAP server and searches for emails from support@wynd.network."""
        try:
            imap_server = EmailUtils.get_imap_server(email_address)

            # Connect to the server
            mail = imaplib.IMAP4_SSL(imap_server)

            # Login to the account
            mail.login(email_address, password)

            # Function to search for the email in a specific mailbox
            def search_in_mailbox(mailbox_name):
                status, _ = mail.select(mailbox_name)
                if status != 'OK':
                    print(f"Failed to select mailbox: {mailbox_name}")
                    return None

                status, messages = mail.search(None, 'FROM', 'support@wyndlabs.ai')
                if status != 'OK':
                    print(f"Failed to search in mailbox: {mailbox_name}")
                    return None
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

                                            if "https://m6zkzl2r.r.us-east-1.awstrack.me/L0/https:%2F%2Fapp.getgrass.io%2Fconfirm-wallet-address%2F%3Ftoken=" in body:
                                                return "https://m6zkzl2r.r.us-east-1.awstrack.me/L0/https:%2F%2Fapp.getgrass.io%2Fconfirm-wallet-address%2F%3Ftoken=" + body.split("https://m6zkzl2r.r.us-east-1.awstrack.me/L0/https:%2F%2Fapp.getgrass.io%2Fconfirm-wallet-address%2F%3Ftoken=")[1].split('"')[0]
                            else:
                                body = msg.get_payload(decode=True)
                                if body:
                                    body = body.decode()

                                    if "https://m6zkzl2r.r.us-east-1.awstrack.me/L0/https:%2F%2Fapp.getgrass.io%2Fconfirm-wallet-address%2F%3Ftoken=" in body:
                                        return "https://m6zkzl2r.r.us-east-1.awstrack.me/L0/https:%2F%2Fapp.getgrass.io%2Fconfirm-wallet-address%2F%3Ftoken=" + body.split("https://m6zkzl2r.r.us-east-1.awstrack.me/L0/https:%2F%2Fapp.getgrass.io%2Fconfirm-wallet-address%2F%3Ftoken=")[1].split('"')[0]
                return None

            verification_link = search_in_mailbox('inbox')
            if verification_link:
                return verification_link

            status, mailboxes = mail.list()
            if status == 'OK':
                for mailbox in mailboxes:
                    mailbox_name = mailbox.decode().split(' "/" ')[-1].strip('"')
                    if 'Spam' in mailbox_name or 'Junk' in mailbox_name or 'spam' in mailbox_name:
                        verification_link = search_in_mailbox(mailbox_name)
                        if verification_link:
                            return verification_link

            mail.logout()
            return ""
        except Exception as e:
            return ""
