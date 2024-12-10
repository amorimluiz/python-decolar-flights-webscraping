from typing import TypedDict
from models.itinerary_model import ItineraryModel

class ItinerariesModel(TypedDict):
  departure_city: str
  arrival_city: str
  outbound: ItineraryModel
  inbound: ItineraryModel