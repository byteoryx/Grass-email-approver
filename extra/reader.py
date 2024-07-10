import base64

import base58
import yaml
from loguru import logger
from mnemonic import Mnemonic
from nacl.encoding import RawEncoder
from nacl.signing import SigningKey
from solders.keypair import Keypair


def read_txt_file(file_name: str, file_path: str) -> list:
    with open(file_path, "r") as file:
        items = [line.strip() for line in file]

    logger.success(f"Successfully loaded {len(items)} {file_name}.")
    return items


def read_config() -> dict:
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    return config


def no_proxies() -> bool:
    user_choice = int(input("No proxies were detected. Do you want to continue without proxies? (1 or 2)\n"
                            "[1] Yes\n"
                            "[2] No\n>> ").strip())

    return True if user_choice == 1 else False


def get_signing_key(private_key_str: str) -> SigningKey:
    # Декодируем приватный ключ из base58
    private_key_bytes = base58.b58decode(private_key_str)
    if len(private_key_bytes) != 64:
        raise ValueError("Invalid private key length")

    # Создаем SigningKey из первых 32 байтов приватного ключа
    signing_key = SigningKey(private_key_bytes[:32])
    return signing_key
