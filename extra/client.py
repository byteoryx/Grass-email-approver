import requests

from model.constants import USER_AGENT


def create_client(proxy: str) -> requests.Session:
    session = requests.Session()

    if proxy:
        session.proxies.update({
            "http": "http://" + proxy,
            "https": "http://" + proxy,
        })

    session.headers.update(HEADERS)

    return session


HEADERS = {
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
    'user-agent': USER_AGENT
}
