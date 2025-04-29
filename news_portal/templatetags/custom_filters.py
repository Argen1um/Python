from django import template
from datetime import datetime
import json, os

register = template.Library()

@register.simple_tag()
def current_time(format_string='%b %d %Y'):
   return datetime.now().strftime(format_string)

@register.filter(name='censor')
def censor(value):
   if not isinstance(value, str):
      return value

   def get_censored_words():
      file_path = os.path.join(os.path.dirname(__file__), 'data', 'censored_words.json')
      try:
         with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('words', [])
      except (FileNotFoundError, json.JSONDecodeError):
         return []

   censored_words = get_censored_words()
   words = value.split()
   censored_text = []

   for word in words:
      # Проверяем слово без учета регистра и знаков пунктуации
      clean_word = ''.join(c for c in word.lower() if c.isalpha())

      if any([w.lower() in clean_word for w in censored_words]):
         # Заменяем все буквы, кроме первой на *
         censored_word = word[0] + '*' * (len(word) - 1)
         censored_text.append(censored_word)
      else:
         censored_text.append(word)
   return ' '.join(censored_text)