from concurrent.futures import ThreadPoolExecutor
from loguru import logger
import threading

import extra
import model


def start():
    def launch_wrapper(index, proxy, account):
        account_flow(lock, index, proxy, account, config, task)

    threads = int(input("How many threads do you want: ").strip())
    task = int(input("Choose the task:\n\n[1] Approve email\n[2] Connect Solana wallet\n\n>> "))

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


def account_flow(lock: threading.Lock, account_index: int, proxy: str, account: str, config: dict, task: int):
    try:
        grass_instance = model.grass.Grass(account, proxy, config)

        ok = wrapper(grass_instance.init_instance, 1)
        if isinstance(ok, bool) and ok:
            pass
        else:
            raise Exception("unable to init grass instance")

        ok = wrapper(grass_instance.login, 1)
        if isinstance(ok, bool) and ok:
            pass
        else:
            raise Exception("login")

        if task == 1:
            ok = wrapper(grass_instance.send_email_verification_link, 1)
            if isinstance(ok, bool) and ok:
                pass
            else:
                raise Exception("send_email_link")

            ok = wrapper(grass_instance.verify_email, 1)
            if isinstance(ok, bool) and ok:
                pass
            else:
                raise Exception("verify_email")

        elif task == 2:
            ok = wrapper(grass_instance.send_wallet_verification_link, 1)
            if isinstance(ok, bool) and ok:
                pass
            else:
                raise Exception("send_wallet_verification_link")

            ok = wrapper(grass_instance.verify_solana_wallet, 1)
            if isinstance(ok, bool) and ok:
                pass
            else:
                raise Exception("verify_solana_wallet")

        with lock:
            with open("data/success_data.txt", "a") as f:
                f.write(f"{account}:{proxy}\n")

    except Exception as err:
        logger.error(f"{account_index} | Account flow failed: {err}")
        with lock:
            report_failed_key(account, proxy, str(err))


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


def report_failed_key(private_key: str, proxy: str, reason: str):
    try:
        with open("data/failed_accounts.txt", "a") as file:
            file.write(private_key + ":" + proxy + ":" + reason + "\n")

    except Exception as err:
        logger.error(f"Error while reporting failed account: {err}")
