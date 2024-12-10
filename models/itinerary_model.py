from typing import TypedDict

class ItineraryModel(TypedDict):
  companies: list[str]
  departure_times: list[str]
  arrival_times: list[str]
  flight_durations: list[str]
  stopovers: list[str]
  departure_airport_iata: str
  arrival_airport_iata: str