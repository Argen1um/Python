import json
import requests
from config import curr

class APIException(Exception):
    pass

class CurrConverter:
    @staticmethod
    def get_price(quote:str, base: str, amount: str):
        try:
            quote_ticker = curr[quote]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: {quote}')
        try:
            base_ticker = curr[base]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: {base}')
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество: {amount}')
        if quote == base:
            raise APIException(f'Невозможно конвертировать две одинаковые валюты {quote}')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        print(json.loads(r.content))

        return json.loads(r.content)[base_ticker] * amount