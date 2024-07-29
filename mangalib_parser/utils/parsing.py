from mangalib_parser.data import SITES
import requests
from mangalib_parser.utils import generate
from mangalib_parser.types import logging

def _get_page_log_info(id, type, page, status):
    
    site = ''
    if type[:1] == 'b':
        site = 'с сайта ' + SITES[type[1:]]
        model = 'закладок'
    elif type == 'f':
        model = 'друзей'
    elif type == 'c':
        model = 'комментариев'
    
    if status == 's':
        return f'Удачное получение {page} страницы {model} пользователя {id} {site}'
    else:
        return f'Неудачное получение {page} страницы {model} пользователя {id} {site}'



def _get_page(
    id: int,
    type: str,
    page: int
):
    headers = generate.headers(type=type)
    
    url = generate.url(id, type=type, page=page)
    
    try:
        response = requests.get(url, headers=headers).json()
        logging.info(_get_page_log_info(id, type, page, 's'))
        return response['data'], response['links']['next']
    
    except requests.exceptions.MissingSchema or requests.exceptions.JSONDecodeError:
        logging.info(_get_page_log_info(id, type, page, 'n'))
        return [] , page