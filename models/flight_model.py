from typing import TypedDict
from models.itineraries_model import ItinerariesModel

class FlightModel(TypedDict):
  amount: float
  url: str
  itineraries: ItinerariesModel