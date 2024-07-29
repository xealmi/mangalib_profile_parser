import requests
from time import sleep
import logging
from datetime import datetime
from mangalib_parser.data import SITES, STATUSES
from mangalib_parser.utils.parsing import _get_page
from mangalib_parser.utils.generate import generate_bookmarks_DataFrame, generate_friends_DataFrame, generate_comments_DataFrame
import os
from pandas import DataFrame

logging.basicConfig(
    level=logging.INFO, filename='mangalib_parser/log.log', filemode='w', encoding='utf-8',
    format='%(asctime)s %(levelname)s %(message)s'
)

def _get_items(
    id: int,
    timeout: float,
    type: str
):
    
    site = ''
    if type[:1] == 'b':
        site = 'с сайта ' + SITES[type[1:]]
        model = 'закладок'
        conv_class = Bookmark
    elif type == 'f':
        model = 'друзей'
        conv_class = Friend
    elif type == 'c':
        model = 'комментариев'
        conv_class = Comment
    
    logging.info(f'Начало парсинга {model} пользователя {id}')
    page = 1
    resp = ''
    clean_list = []
    
    while resp != None:
        data, resp = _get_page(id, type, page)
        clean_list.append(data)
        page+=1
        
        sleep(timeout) 
    
    clean_list.append(data)
    
    logging.info(f'Окончание парсинга {model} пользователя {id}, начало преобразования их в класс {conv_class} {site}')
    
    result = []
    
    for list in clean_list:
        for item in list:
            result.append(conv_class(item))
    
    logging.info(f'Все из {model} пользователя {id} успешно преобразованы в класс {conv_class}\n' + ' '*28 + f'Всего: {len(result)}')
    
    return result

class Comment:
    def __init__(
        self,
        comment: dict
    ):
        self.text = comment['comment'].replace('<p>', '').replace('</p>', '')
        self.created_at = comment['created_at'][:-8].replace('T', ' ')
        if 'manga' in comment['relation']:
            self.title_name = comment['relation']['manga']['name']
            self.title_rus_name = comment['relation']['manga']['rus_name']
            self.title_eng_name = comment['relation']['manga']['eng_name']
            self.site_id = comment['relation']['manga']['site']
            self.number = comment['relation']['number']
            self.page = comment['post_page']
            self.url = f'https://{SITES[str(self.site_id)]}/ru/{comment['relation']['manga']['slug_url']}/read/v{comment['relation']['number_secondary']}/c{self.number}?bid={comment['relation']['branch_id']}&comment_id={comment['id']}&p={self.page}'
        else:
            self.title_name =  ''
            self.title_rus_name = ''
            self.title_eng_name = ''
            self.site_id = ''
            self.number = ''
            self.page = ''
            self.url = ''
        self.user_id = comment['user']['id']
        self.user_username = comment['user']['username']
        self.rating = comment['votes']['up'] - comment['votes']['down']



class CommentsList:
    def __init__(
        self,
        comlist: list[Comment]
    ):
        self.texts = []
        self.created_at_s = []
        self.title_names = []
        self.title_rus_names = []
        self.title_eng_names = []
        self.site_ids = []
        self.numbers = []
        self.pages = []
        self.urls = []
        self.user_ids = []
        self.user_usernames = []
        self.ratings = []
        for i in comlist:
            self.texts.append(i.text)
            self.created_at_s.append(i.created_at)
            self.title_names.append(i.title_name)
            self.title_rus_names.append(i.title_rus_name)
            self.title_eng_names.append(i.title_eng_name)
            self.site_ids.append(i.site_id)
            self.numbers.append(i.number)
            self.pages.append(i.page)
            self.urls.append(i.url)
            self.user_ids.append(i.user_id)
            self.user_usernames.append(i.user_username)
            self.ratings.append(i.rating)



class Friend:
    def __init__(
        self,
        info: dict
    ):
        self.id = info['id']
        self.comment = info['comment']
        self.created_at = info['created_at'][:-8].replace('T', ' ')
        self.is_awaiting_confirmation = info['status']['is_awaiting_confirmation']
        self.is_friend = info['status']['is_friend']
        self.is_requested = info['status']['is_requested']
        self.username = info['user']['username']
        self.url = f'https://test-front.mangalib.me/ru/user/{self.id}'



class FriendsList:
    def __init__(
        self,
        frilist: list[Friend]
    ):
        self.ids = []
        self.comments = []
        self.created_at_s = []
        self.is_awaiting_confirmation_s = []
        self.is_friends = []
        self.is_requesteds = []
        self.usernames = []
        self.urls = []
        
        for i in frilist:
            self.ids.append(i.id)
            self.comments.append(i.comment)
            self.created_at_s.append(i.created_at)
            self.is_awaiting_confirmation_s.append(i.is_awaiting_confirmation)
            self.is_friends.append(i.is_friend)
            self.is_requesteds.append(i.is_requested)
            self.usernames.append(i.username)
            self.urls.append(i.url)



class Bookmark:
    def __init__(
        self,
        bookmark: dict
    ):
        self.name = bookmark['media']['name']
        self.rus_name = bookmark['media']['rus_name']
        self.eng_name = bookmark['media']['eng_name']
        self.age_restriction = bookmark['media']['ageRestriction']['label']
        self.status_id = bookmark['status']
        self.status = STATUSES[str(self.status_id)]
        self.type_id = bookmark['media']['type']['id']
        self.type = bookmark['media']['type']['label']
        self.number = bookmark['meta']['item_number'] if bookmark['meta'] != None else '-'
        self.page = bookmark['progress']
        self.rating = bookmark['rating'] if bookmark['rating'] != None else '-'
        self.updated_at = bookmark['updated_at']
        self.created_at = bookmark['created_at']
        self.site_id = bookmark['media']['site']
        self.url = f'https://{SITES[str(self.site_id)]}/ru/{bookmark['media']['model']}/{bookmark['media']['slug_url']}'



class BookmarksList:
    def __init__(
        self,
        bmlist: list[Bookmark]
    ):
        
        self.names = []
        self.rus_names = []
        self.eng_names = []
        self.age_restrictions = []
        self.status_ids = []
        self.statuses = []
        self.type_ids = []
        self.types = []
        self.numbers = []
        self.pages = []
        self.ratings = []
        self.updated_at_s = []
        self.created_at_s = []
        self.site_ids = []
        self.urls = []
        for i in bmlist:
            self.names.append(i.name)
            self.rus_names.append(i.rus_name)
            self.eng_names.append(i.eng_name)
            self.age_restrictions.append(i.age_restriction)
            self.status_ids.append(i.status_id)
            self.statuses.append(i.status)
            self.type_ids.append(i.type_id)
            self.types.append(i.type)
            self.numbers.append(i.number)
            self.pages.append(i.page)
            self.ratings.append(i.rating)
            self.updated_at_s.append(i.updated_at)
            self.created_at_s.append(i.created_at)
            self.site_ids.append(i.site_id)
            self.urls.append(i.url)

class User:
    def __init__(
        self,
        id: int | str
    ):
        logging.info(f'Начало попытки получить данные об аккаунте {id}')
        try:
            response: dict = requests.get(f'https://api.lib.social/api/user/{id}?fields[]=background&fields[]=roles&fields[]=points&fields[]=ban_info&fields[]=gender&fields[]=created_at&fields[]=about&fields[]=teams').json()
        except requests.exceptions.MissingSchema:
            logging.info(f'Неудача попытки получить данные об аккаунте {id}: неверный id')
            raise ValueError('Invalid ID')
        
        logging.info(f'Успешное получение данных об аккаунте {id}')
        data = response['data']
        
        self.id: int = id
        self.username : str = data['username']
        self.about = data['about']
        self.gender : str = data['gender']['label']
        self.gender_id : int = data['gender']['id']
        self.last_online : str = data['last_online_at'][:-8].replace('T', ' ')
        self.created_date : str = data['created_at'][:-8].replace('T', ' ')
        self.level : int = data['points_info']['level']
        self.total_points : int = data['points_info']['total_points']
        self.top : None | int = data['points_info']['top']
        self.ban_info = data['ban_info']
        self.eng_role = [role['name'] for role in data['roles']] if data['roles'] != [] else []
        self.rus_role = [role['rus_name'] for role in data['roles']] if data['roles'] != [] else []
        self.avatar_url = data['avatar']['url']
        self.background_url = data['background']['url']
    
    
    
    def get_mangalib_bookmark(self, timeout: float = 0) -> BookmarksList:
        return BookmarksList(_get_items(self.id, timeout, 'b1'))
    
    
    
    def get_slashlib_bookmark(self, timeout: float = 0) -> BookmarksList:
        return BookmarksList(_get_items(self.id, timeout, 'b2'))
    
    
    
    def get_ranobelib_bookmark(self, timeout: float = 0) -> BookmarksList:
        return BookmarksList(_get_items(self.id, timeout, 'b3'))
    
    
    
    def get_hentailib_bookmark(self, timeout: float = 0) -> BookmarksList:
        return BookmarksList(_get_items(self.id, timeout, 'b4'))
    
    
    
    def get_comments(self, timeout: float = 0) -> CommentsList:
        return CommentsList(_get_items(self.id, timeout, 'c'))
    
    
    
    def get_friends(self, timeout: float = 0) -> FriendsList:
        return FriendsList(_get_items(self.id, timeout, 'f'))
    
    
    
    def save_data(self):
        
        '''
            Сохраняет все данные о пользователе в папку data/{id_пользователя}__{число}_{месяц}_{год}_{час}_{минута}
        '''
        
        if not os.path.exists('data'):
            os.mkdir('data')
            os.mkdir('data/' + str(self.id))
        
        if not os.path.exists(str(self.id)):
            os.mkdir('data/' + str(self.id))
        
        path = f'data/{self.id}/{self.id}__{datetime.now().strftime('%d_%m_%Y_%H_%M')}'
        
        os.mkdir(path)
        os.mkdir(path + '/bookmarks')
        
        for site in ['b1', 'b2', 'b3', 'b4']:
            if site == 'b1':
                s = 'mangalib'
            elif site == 'b2':
                s = 'slashlib'
            elif site == 'b3':
                s = 'ranobelib'
            elif site == 'b4':
                s = 'hentailib'
            
            frame = generate_bookmarks_DataFrame(BookmarksList(_get_items(self.id, 0, site)))
            frame.to_excel(path + '/bookmarks/' + f'{s}.xlsx', index=False)
        
        
        frame = generate_comments_DataFrame(CommentsList(_get_items(self.id, 0, 'c')))
        frame.to_excel(path + f'/comments.xlsx', index=False)
        
        
        frame = generate_friends_DataFrame(FriendsList(_get_items(self.id, 0, 'f')))
        frame.to_excel(path + f'/friends.xlsx', index=False)
        
        
        frame = DataFrame(
            {
                'Характеристика': ['Ник', 'Id', 'Пол', 'Описание', 'Онлайн', 'Уровень', 'Дата создания'],
                'Значение': [self.username, self.id, self.gender, self.about, self.last_online, self.level, self.created_date]
            }
        )
        frame.to_excel(path + f'/profile.xlsx', index=False)