from eth_account.messages import encode_defunct
import requests
from datetime import datetime
from loguru import logger
from web3 import Web3
import eth_account
import time

from extra.client import create_client
from extra.email_utils import EmailUtils
from model.utils import retry


class Grass:
    def __init__(self, account: str, proxy: str, config: dict):
        self.account = account
        self.private_key = ""
        self.account_email = ""
        self.email_password = ""
        self.account_password = ""
        self.proxy = proxy
        self.config = config

        self.client: requests.Session | None = None

        self.access_token = ""
        self.refresh_token = ""
        self.user_id = ""
        self.email_verify_link = ""

    def init_instance(self):
        for _ in range(5):
            try:
                if "dmail" in self.account:
                    self.account_email = self.account.split(":")[0]
                    self.private_key = self.account.split(":")[1]
                    self.account_password = self.account.split(":")[2]
                else:
                    self.account_email = self.account.split(":")[0]
                    self.email_password = self.account.split(":")[1]
                    self.account_password = self.account.split(":")[2]

                self.client = create_client(self.proxy)

                return True
            except Exception as err:
                logger.error(f"{self.account_email} | Failed to init client: {err}")

        return False

    @retry(5, lambda self: self.__get_log_indicator())
    def login(self) -> bool:
        try:
            headers = {
                'accept': '*/*',
                'content-type': 'text/plain;charset=UTF-8',
                'origin': 'https://app.getgrass.io',
                'priority': 'u=1, i',
                'referer': 'https://app.getgrass.io/',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }

            data = '{"username":"' + self.account_email + '","password":"' + self.account_password + '"}'

            response = self.client.post('https://api.getgrass.io/login', headers=headers, data=data, verify=False)

            self.access_token = response.json()['result']['data']['accessToken']
            self.refresh_token = response.json()['result']['data']['refreshToken']
            self.user_id = response.json()['result']['data']['userId']

            logger.success(f"{self.account_email} | Successfully logged in.")

            return True
        except Exception as err:
            logger.error(f"{self.account_email} | Failed to login Grass: {err}")
            raise

    @retry(5, lambda self: self.__get_log_indicator())
    def send_email_verification_link(self) -> bool:
        try:
            headers = {
                'accept': 'application/json, text/plain, */*',
                'authorization': self.access_token,
                'content-type': 'application/json',
                'origin': 'https://app.getgrass.io',
                'priority': 'u=1, i',
                'referer': 'https://app.getgrass.io/',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }

            json_data = {
                'email': self.account_email,
            }

            response = self.client.post('https://api.getgrass.io/sendEmailVerification', headers=headers, json=json_data, verify=False)

            if response.json()['result'] == {} and 200 <= response.status_code < 400:
                logger.success(f"{self.account_email} | The verification link has been sent to email.")
                return True
            else:
                raise Exception(f"status code: {response.status_code}")

        except Exception as err:
            logger.error(f"{self.account_email} | Failed to get verification link: {err}")
            raise

    @retry(5, lambda self: self.__get_log_indicator())
    def verify_email(self) -> bool:
        try:
            verified = self._check_if_email_verified()
            if verified:
                return True

            time.sleep(15)
            if self.email_verify_link == "":
                for retry in range(15):
                    if "dmail" in self.account:
                        link = self.get_dmail_code()
                    else:
                        email_utils = EmailUtils()
                        link = email_utils.get_verification_link(self.account_email, self.email_password)

                    if link == "":
                        time.sleep(20)
                        continue

                    self.email_verify_link = link
                    logger.success(f"{self.account_email} | Got email link!")
                    break

            if self.email_verify_link == "":
                raise Exception("timeout waiting for email link")

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'priority': 'u=0, i',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }
            token = self.email_verify_link.split("token&#x3D;")[1]

            params = {
                'token': token,
            }

            self.client.get('https://app.getgrass.io/confirm-email', params=params, headers=headers, verify=False)

            headers = {
                'accept': 'application/json, text/plain, */*',
                'authorization': self.access_token,
                'content-type': 'application/json',
                'origin': 'https://app.getgrass.io',
                'priority': 'u=1, i',
                'referer': 'https://app.getgrass.io/',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }

            json_data = {}

            self.client.post('https://api.getgrass.io/confirmEmail', headers=headers, json=json_data, verify=False)

            time.sleep(2)

            verified = self._check_if_email_verified()

            if verified:
                return True
            else:
                return False

        except Exception as err:
            logger.error(f"{self.account_email} | Failed to verify email: {err}")
            raise

    @retry(5, lambda self: self.__get_log_indicator())
    def get_dmail_code(self):
        try:
            headers = {
                'accept': 'application/json, text/plain, */*',
                'origin': 'https://mail.dmail.ai',
                'priority': 'u=1, i',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }

            response = self.client.get('https://icp.dmail.ai/api/node/v6/dmail/auth/generate_nonce', headers=headers)
            if not response.json()['success']:
                raise Exception("unable to get nonce")

            nonce = response.json()['data']['nonce']

            wallet = eth_account.Account().from_key(self.private_key)
            address = wallet.address

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message_to_sign = (
                "SIGN THIS MESSAGE TO LOGIN TO THE INTERNET COMPUTER\n\n"
                "APP NAME: \ndmail\n\n"
                f"ADDRESS: \n{address.lower()}\n\n"
                f"NONCE: \n{nonce}\n\n"
                f"CURRENT TIME: \n{current_time}"
            )

            signature = self.__get_signature(message_to_sign)

            json_data = {
                "message":
                    {
                        "Message": "SIGN THIS MESSAGE TO LOGIN TO THE INTERNET COMPUTER",
                        "APP NAME": "dmail",
                        "ADDRESS": address.lower(),
                        "NONCE": nonce,
                        "CURRENT TIME": current_time
                    },
                "signature": signature,
                "wallet_name": "metamask",
                "chain_id": 1
            }

            headers = {
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json',
                'origin': 'https://mail.dmail.ai',
                'priority': 'u=1, i',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }

            response = self.client.post('https://icp.dmail.ai/api/node/v6/dmail/auth/evm_verify_signature', headers=headers, json=json_data)

            if not response.json()['success']:
                raise Exception("wrong server response")

            dmail_pid = response.json()['data']['pid']
            dmail_token = response.json()['data']['token']

            headers = {
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json',
                'dm-encstring': dmail_token,
                'dm-pid': dmail_pid,
                'origin': 'https://mail.dmail.ai',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }

            json_data = {
                'dm_folder': 'inbox',
                'store_type': 'mail',
                'pageInfo': {
                    'page': 1,
                    'pageSize': 20,
                },
            }

            response = self.client.post(
                'https://icp.dmail.ai/api/node/v6/dmail/inbox_all/read_by_page_with_content',
                headers=headers,
                json=json_data,
            )

            if not response.json()['success']:
                raise Exception("unable to get dmail inbox messages")

            messages = response.json()['data']['list']

            for message in messages:
                message_content = message['content']['html']
                if "https://app.getgrass.io/confirm-email/?token" in message_content:
                    return "https://app.getgrass.io/confirm-email/?token" + message_content.split("https://app.getgrass.io/confirm-email/?token")[1].split('"')[0]

            raise Exception("no link found in dmail messages")

        except Exception as err:
            logger.error(f"{self.account_email} | Dmail login failed: {err}")
            raise

    def _check_if_email_verified(self) -> bool:
        try:
            headers = {
                'accept': 'application/json, text/plain, */*',
                'authorization': self.access_token,
                'origin': 'https://app.getgrass.io',
                'priority': 'u=1, i',
                'referer': 'https://app.getgrass.io/',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }

            response = self.client.get('https://api.getgrass.io/retrieveUser', headers=headers, verify=False)

            if '"isVerified":true' in response.text:
                logger.success(f"{self.account_email} | Email verified!")
                return True
            else:
                return False

        except Exception as err:
            logger.error(f"{self.account_email} | Failed to check if email verified: {err}")
            raise

    def __get_signature(self, message: str):
        encoded_msg = encode_defunct(text=message)
        signed_msg = Web3().eth.account.sign_message(encoded_msg, private_key=self.private_key)
        return signed_msg.signature.hex()

    def __get_log_indicator(self):
        return self.account_email
