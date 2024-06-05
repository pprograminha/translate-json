import json
import os
import openai

openai.api_key = 'YOUR_API_KEY'

BASE_LOCALE = 'en'
LOCALES_PATH = '../../locales'


def is_valid_json(json_string: str):
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False

def get_locale_json(locale_path: str):
  with open(f"{locale_path}", 'r', encoding='utf-8') as locale_data:
    data: dict[str, str] = json.load(locale_data)
  
  return data

def get_diff_between(json: dict[str, str], json_to_compare: dict[str, str]):
    diff_json: dict[str, str] = {}
    
    for key in json_to_compare:
      if(key not in json):
        diff_json[key] = json_to_compare[key]

    return diff_json

def main():
  locales = os.listdir(LOCALES_PATH)

  base_locale_json = get_locale_json(f"{LOCALES_PATH}/{BASE_LOCALE}.json")

  for locale in locales:
    locale_name, locale_type = locale.split('.')

    if(locale_name == BASE_LOCALE or locale_type != 'json'): 
      continue

    locale_json = get_locale_json(f"{LOCALES_PATH}/{locale}")

    diff_json = get_diff_between(locale_json, base_locale_json)

    for i, key in enumerate(diff_json.copy(), 0):
      if(i > 50):
        diff_json.pop(key)
    
    if(len(diff_json) == 0):
      print(f'Não há diferença entre ({locale_name}) e ({BASE_LOCALE}).')
      continue
    else: 
      print(f'Diferença de {len(diff_json)} entre ({locale_name}) e ({BASE_LOCALE}).')

    prompt = f'Você é um assistente de tradução de texto. Mantenha as KEYS. O retorno JSON deve ser sempre em aspas duplas "". Traduza para o idioma ({locale_name}). Responda em formato JSON: {diff_json}'

    response = openai.chat.completions.create(
      model="gpt-3.5-turbo-0613",
      messages=[
        {
          'content': prompt,
          'role': 'system'
        }
      ],
    )

    json_string = response.choices[0].message.content

    try:
      if json_string is not None and is_valid_json(json_string):
        json_data: dict[str, str] = json.loads(json_string)
        json_data_copy = json_data.copy()

        for key in json_data:
          if(key not in base_locale_json):
            del json_data[key]

        if(len(json_data) > 0):
          for key in json_data:
            locale_json[key] = json_data[key]

            with open(f"{LOCALES_PATH}/{locale}", 'w') as file:
              json.dump(locale_json, file, indent=4, ensure_ascii=False)
          
        print(f'Valores ignorados: {len(json_data_copy) - len(json_data)}')
        print(f'Valores adicionados: {len(json_data)}')
      else: 
        print('JSON inválido', json_string)
    except Exception as err:
      print('Ocorreu um erro ao tentar traduzir', err)
        
    
main()