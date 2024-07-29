from mangalib_parser.types import User

with open('users.txt', 'r', encoding='utf-8') as file:
    data = file.read().split()

for user_id in data:
    user = User(user_id)

    user.save_data()