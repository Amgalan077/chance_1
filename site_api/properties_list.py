import requests


def print_hotels(hotel_id):
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
        "X-RapidAPI-Key": "e0cc7fd92emsh263002a07577720p1228b3jsn969f9bf74c83",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())