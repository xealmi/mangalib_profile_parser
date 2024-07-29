from mangalib_parser import data
from pandas import DataFrame

def url(id, type, page) -> str:
    if type[:1] == 'b':
        url = f'http://api.lib.social/api/bookmarks?page={page}&sort_by=updated_at&sort_type=desc&status=0&user_id={id}'
    elif type == 'f':
        url = f"https://api.lib.social/api/friendship?page={page}&status=1&user_id={id}"
    elif type == 'c':
        url = f"https://api.lib.social/api/user/{id}/comments?page={page}&sort_by=id&sort_type=desc"
    
    return url

def headers(type):
    headers = data.HEADERS
    
    if type[:1] == 'b':
        site = int(type[1:])
        
        headers['site-id'] = str(site)
        headers['origin'] = 'https://' + data.SITES[str(site)]
        headers['referer'] = 'https://' + data.SITES[str(site)] + '/'
    
    return headers

def generate_bookmarks_DataFrame(bmlist) -> DataFrame:
    
    res = {
        'Название': bmlist.rus_names,
        'Статус': bmlist.statuses,
        'Глава': bmlist.numbers,
        'Страница': bmlist.pages,
        'Посл. закладка': bmlist.updated_at_s,
        'Дата добавления': bmlist.created_at_s,
        'Ссылка': bmlist.urls,
        'Возр. огр': bmlist.age_restrictions,
        'Оценка': bmlist.ratings
    }
    
    return DataFrame(res)



def generate_comments_DataFrame(comlist) -> DataFrame:
    res = {
        'Комментарий': comlist.texts,
        'Дата создания': comlist.created_at_s,
        'Тайтл': comlist.title_rus_names,
        'Рейтинг': comlist.ratings,
        'Ссылка': comlist.urls
    }
    
    return DataFrame(res)



def generate_friends_DataFrame(frilist) -> DataFrame:
    res = {
        'Имя': frilist.usernames,
        'Комментарий': frilist.comments,
        'Дата создания': frilist.created_at_s,
        'ДругИлиНет': frilist.is_friends,
        'Ссылка': frilist.urls
    }
    
    return DataFrame(res)