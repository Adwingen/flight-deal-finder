from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
import datetime as dt
import time
from notification_manager import NotificationManager



ORIGIN_CITY_IATA = "LON"

data_manager = DataManager()
flight_search = FlightSearch()
sheet_data = data_manager.get_destination_data()
notification_manager = NotificationManager()

tomorrow = dt.datetime.now() + dt.timedelta(days=1)
six_months_later = dt.datetime.now() + dt.timedelta(days=6*30)

for destination in sheet_data:
    if destination.get("iataCode") and destination["iataCode"] != ORIGIN_CITY_IATA:
        flight = flight_search.check_flights(
            origin_city_code=ORIGIN_CITY_IATA,
            destination_city_code=destination["iataCode"],
            from_time=tomorrow,
            to_time=six_months_later
        )
        print(f"{destination['city']}: £{flight.price}")

        if flight.price != "N/A" and float(flight.price) < float(destination["lowestPrice"]):
            msg = (
                f"🛫 Nova oportunidade de voo!\n"
                f"Preço: £{flight.price}\n"
                f"De: {flight.origin_city} ({flight.origin_airport})\n"
                f"Para: {flight.destination_city} ({flight.destination_airport})\n"
                f"Ida: {flight.out_date}\n"
                f"Volta: {flight.return_date}"
            )
            notification_manager.send_sms(msg)

        time.sleep(1.1)




