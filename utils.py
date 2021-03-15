import re
import random
import requests
from typing import (
    List, Dict, Tuple, 
    Iterable, Any, Type, 
    Union
)

RequestsResponse = requests.models.Response


def err(e: str) -> None:
    """ Close with error info
    """
    input(e)
    exit()


def net_to_cookie(filename: str, service: str) -> Dict[str, str]:
    """ Netscape cookies to python dict
    """
    cookies = {}
    try:
        with open(filename, 'r', encoding='utf-8') as fp:
            for line in fp:
                try:
                    if not re.match(r'^\#', line) and service in line:
                        lineFields = line.strip().split('\t')
                        cookies[lineFields[5]] = lineFields[6]
                except Exception:
                    pass
    except UnicodeDecodeError:
        with open(filename, 'r') as fp:
            for line in fp:
                try:
                    if not re.match(r'^\#', line) and service in line:
                        lineFields = line.strip().split('\t')
                        cookies[lineFields[5]] = lineFields[6]
                except Exception:
                    pass
    return cookies


def dict_cookies_to_str(cookie: dict) -> str:
    """ Refactoring dict cookies to str
    """
    str_cookie = ""
    for key, value in cookie.items():
        str_cookie += f"{key}={value}; "
    return str_cookie


def get_random_proxy(proxies: list, proxy_type: str) -> Dict[str, str]:
    """ Retrieving and refactoring proxies
    """
    random_proxy = random.choice(proxies)
    try:
        ip, port, username, password = random_proxy.split(':')
        return {
            'http': f'{proxy_type}://{username}:{password}@{ip}:{port}',
            'https': f'{proxy_type}://{username}:{password}@{ip}:{port}'}
    except:
        return {
            'http': f'{proxy_type}://{random_proxy}',
            'https': f'{proxy_type}://{random_proxy}'}
        
        
def get_proxies_from_file(file_name: str) -> List[str]:
    """ Getting proxies from file
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as pf:
            proxies = pf.read().splitlines()
            if proxies:
                return proxies
            else:
                err(f"where is the proxies in {file_name}?")
    except FileNotFoundError:
        err(f"File {file_name} not found")
    except Exception:
        err(f"Error while getting proxy from {file_name}")
        
        
def connection(obj: RequestsResponse, url: str, proxies: list, 
               proxy_type: str, **kwargs) -> str:
    """ Superstructure over requests
    """
    conn_counter = 50
    while conn_counter > 0:
        try:
            proxy = get_random_proxy(proxies, proxy_type)
            r = obj(url=url, **kwargs)
            print(r.status_code)
            if r.status_code == 200 and r.text:
                return r
            elif r.status_code == 403:
                return
            else:
                try:
                    response_data = r.json()
                    if response_data['status'] == 'fail':
                        return
                except:
                    pass
            conn_counter -= 1
        except requests.RequestException as e:
            print(e)
            conn_counter -= 1
        except Exception as e:
            print(e)
            conn_counter -= 1