from mangalib_parser.types import User

with open('users.txt', 'r', encoding='utf-8') as file:
    data = file.read().split()

while True:
    form = input('Выберите формат сохранения:\n1>.xlsx\n2>.csv\n')
    if form == '1':
        format = 'xlsx'
        break
    elif form == '2':
        format = 'csv'
        break
    else:
        print('Ответ не распознан, введите ещё раз.\n')

for user_id in data:
    user = User(user_id)

    user.save_data(format)