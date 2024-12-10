from typing import TypedDict

class ScrapeParamsModel(TypedDict):
  departure_airport_iata: str
  departure_date: str
  return_airport_iata: str
  return_date: str
  maximum_price: float