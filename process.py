from concurrent.futures import ThreadPoolExecutor
from loguru import logger
import threading

import extra
import model


def start():
    def launch_wrapper(index, proxy, account):
        account_flow(lock, index, proxy, account, config)

    threads = int(input("How many threads do you want: ").strip())

    config = extra.read_config()

    proxies = extra.read_txt_file("proxies", "data/proxies.txt")
    accounts = extra.read_txt_file("accounts", "data/accounts.txt")
    indexes = [i + 1 for i in range(len(accounts))]

    use_proxy = True
    if len(proxies) == 0:
        if not extra.no_proxies():
            return
        else:
            use_proxy = False

    lock = threading.Lock()

    if not use_proxy:
        proxies = ["" for _ in range(len(accounts))]
    elif len(proxies) < len(accounts):
        proxies = [proxies[i % len(proxies)] for i in range(len(accounts))]

    logger.info("Starting...")
    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(launch_wrapper, indexes, proxies, accounts)

    logger.success("Saved accounts and private keys to a file.")


def account_flow(lock: threading.Lock, account_index: int, proxy: str, account: str, config: dict):
    try:
        grass_instance = model.grass.Grass(account, proxy, config)

        ok = wrapper(grass_instance.init_instance, 1)
        if not ok:
            raise Exception("unable to init grass instance")

        ok = wrapper(grass_instance.login, 1)
        if not ok:
            raise Exception("unable to login")

        ok = wrapper(grass_instance.send_email_verification_link, 1)
        if not ok:
            raise Exception("unable to send email link")

        ok = wrapper(grass_instance.verify_email, 1)
        if not ok:
            raise Exception("unable to verify_email")

        with lock:
            with open("data/success_data.txt", "a") as f:
                f.write(f"{account}:{proxy}\n")

    except Exception as err:
        logger.error(f"{account_index} | Account flow failed: {err}")
        with lock:
            report_failed_key(account, proxy)


def wrapper(function, attempts: int, *args, **kwargs):
    for _ in range(attempts):
        result = function(*args, **kwargs)
        if isinstance(result, tuple) and result and isinstance(result[0], bool):
            if result[0]:
                return result
        elif isinstance(result, bool):
            if result:
                return True

    return result


def report_failed_key(private_key: str, proxy: str):
    try:
        with open("data/failed_accounts.txt", "a") as file:
            file.write(private_key + ":" + proxy + "\n")

    except Exception as err:
        logger.error(f"Error while reporting failed account: {err}")
