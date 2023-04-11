import requests
from config import API_KEY


class APIException(Exception):
    pass


class UserEnter(ValueError):
    pass


class Converter:
    @staticmethod
    def get_price(to: str, fr: str, amount: int) -> dict:
        url = f"https://api.apilayer.com/fixer/convert?to={to}&from={fr}" \
              f"&amount={amount}"

        payload = {}
        headers = {
            "apikey": API_KEY
        }
        try:
            response = requests.request("GET", url, headers=headers,
                                        data=payload)

            status_code = response.status_code
            if status_code == 200:
                result = response.json()
                return result
            else:
                raise APIException()
        except APIException as e:
            print('Ошибка запроса', e)
