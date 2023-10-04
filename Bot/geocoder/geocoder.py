from aiohttp import ClientSession
from Bot.config import YANDEX_GEOCODER_KEY
from pprint import pprint


async def get_place_coord(place_name: str, api_key: str = YANDEX_GEOCODER_KEY) -> dict | None:
    """
    Возвращает координаты места по его названию в виде словаря {'lat': float, 'lon': float, 'place': str}.
    В случае неудачи вернет None.
    """
    url = "https://geocode-maps.yandex.ru/1.x"
    req_params = {
        "geocode": place_name,
        "apikey": api_key,
        "format": "json"
    }
    async with ClientSession() as session:
        async with session.get(url, params=req_params) as response:
            if response.status == 200:
                res = await response.json()
                # Получаем первый найденный объект
                try:
                    first_obj = res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                except IndexError:
                    return None
                # Берем его координаты, название места и возвращаем юзеру
                coord = first_obj['Point']["pos"].split()
                place_descr = first_obj['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']
                address = place_descr['AddressLine']
                return {'lat': coord[1], 'lon': coord[0], 'place': address}
            else:
                return None

