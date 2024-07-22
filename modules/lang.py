from modules import database
import json

def get_translation(key, user_id):
    language = database.select(f"select locale from users where id = {user_id}", one=True)[0]
    with open(f'lang/{language}.json', 'r', encoding='utf-8') as file:
        translations = json.load(file)
    return translations.get(key, '')

