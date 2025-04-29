import os
import requests
from dotenv import load_dotenv
from flight_data import FlightData
import datetime as dt

# Carregar variáveis do .env
load_dotenv()

# Constantes da API Amadeus
TOKEN_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"
IATA_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations"

class FlightSearch:
    """
    Classe responsável por interagir com a Amadeus API para obter códigos IATA.
    """

    def __init__(self):
        self._api_key = os.environ["AMADEUS_API_KEY"]
        self._api_secret = os.environ["AMADEUS_API_SECRET"]
        self._token = self._get_new_token()

    def _get_new_token(self):
        """
        Obtém um novo token de autenticação (Bearer) da Amadeus API.
        Retorna:
            str: token de acesso válido.
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret
        }
        response = requests.post(url=TOKEN_ENDPOINT, headers=headers, data=body)
        response.raise_for_status()

        data = response.json()
        print(f"[DEBUG] Token obtido com sucesso (expira em {data['expires_in']}s)")
        return data["access_token"]

    def get_destination_code(self, city_name):
        """
        Pesquisa o código IATA de uma cidade.
        Args:
            city_name (str): Nome da cidade (ex: "Lisbon")
        Returns:
            str: Código IATA (ex: "LIS"), ou "" se não encontrado.
        """
        headers = {"Authorization": f"Bearer {self._token}"}
        params = {
            "keyword": city_name,
            "subType": "CITY"
        }

        response = requests.get(
            url=IATA_ENDPOINT,
            headers=headers,
            params=params
        )

        print(f"[DEBUG] {city_name} → Status {response.status_code}")
        print(f"[DEBUG] Resposta: {response.text}")

        try:
            code = response.json()["data"][0]["iataCode"]
            print(f"[INFO] Código IATA para {city_name}: {code}")
            return code
        except IndexError:
            print(f"[ERRO] Nenhum resultado encontrado para '{city_name}'.")
            return ""
        except KeyError:
            print(f"[ERRO] Resposta inesperada da API para '{city_name}'.")
            return ""

    def check_flights(self, origin_city_code, destination_city_code, from_time, to_time):
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

        headers = {
            "Authorization": f"Bearer {self._token}"
        }

        params = {
            "originLocationCode": origin_city_code,
            "destinationLocationCode": destination_city_code,
            "departureDate": from_time.strftime("%Y-%m-%d"),
            "returnDate": to_time.strftime("%Y-%m-%d"),
            "adults": 1,
            #"nonStop": True,
            "max": 1,
            "currencyCode": "GBP"
        }

        response = requests.get(url, headers=headers, params=params)

        print(f"[DEBUG] Procurando voo de {origin_city_code} para {destination_city_code}")
        print(f"[DEBUG] Status: {response.status_code}")

        if response.status_code != 200:
            print(f"[ERRO] Falha na pesquisa: {response.text}")
            return FlightData("N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

        data = response.json()
        try:
            offer = data["data"][0]
            price = offer["price"]["total"]

            itinerary = offer["itineraries"][0]["segments"][0]
            return_itinerary = offer["itineraries"][1]["segments"][0]

            flight_data = FlightData(
                price=price,
                origin_city=itinerary["departure"]["iataCode"],
                origin_airport=itinerary["departure"]["iataCode"],
                destination_city=itinerary["arrival"]["iataCode"],
                destination_airport=itinerary["arrival"]["iataCode"],
                out_date=itinerary["departure"]["at"].split("T")[0],
                return_date=return_itinerary["departure"]["at"].split("T")[0]
            )
            return flight_data

        except (IndexError, KeyError):
            print(f"[ERRO] Nenhum voo encontrado para {destination_city_code}")
            return FlightData("N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")



