
import requests


def get_city_id(city_name):
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": f"{city_name}", "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}

    headers = {
        "X-RapidAPI-Key": "d286ed94e3msh948f528a9792a55p1034b5jsn11cffe61f435",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()

    data_id = data['sr'][0]['gaiaId']

    return data_id


def get_hotels_in_city(city_id, num_hotels,sort_ = 'low', min_price: int = 1, max_price: int = 100):
    list_hotels = {}

    if sort_ == 'low':
        sort_key = 'PRICE_LOW_TO_HIGH'
    else:
        sort_key = 'RECOMMENDED'


    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": f"{get_city_id(city_id)}"},
        "checkInDate": {
            "day": 10,
            "month": 10,
            "year": 2022
        },
        "checkOutDate": {
            "day": 15,
            "month": 10,
            "year": 2022
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": f"{sort_key}", #
        "filters": {"price": {
            "max": max_price,
            "min": min_price
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "d286ed94e3msh948f528a9792a55p1034b5jsn11cffe61f435",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    properties = data['data']['propertySearch']['properties']


    try:
        for i in range(num_hotels):
            list_hotels[f"Отель: {properties[i]['name']}. Цена: {properties[i]['price']['lead']['formatted']}"] = properties[i]['id']
    except IndexError:
        # list_hotels += 'Все, что есть'
        return list_hotels
    return list_hotels


def print_hotels(hotel_id, num_photo):
    list_photo = {}
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": f"{hotel_id}"
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "d286ed94e3msh948f528a9792a55p1034b5jsn11cffe61f435",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    for i in range(num_photo):
        list_photo[f"{data['data']['propertyInfo']['propertyGallery']['images'][i]['image']['description']}"] = data['data']['propertyInfo']['propertyGallery']['images'][i]['image']['url']

    return list_photo
