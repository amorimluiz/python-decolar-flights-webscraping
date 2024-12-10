from models.flight_model import FlightModel

class FlightService:

  async def __sanitize_dict_string_values(self, value: str | list | dict) -> dict:
    if isinstance(value, dict):
      return {key: await self.__sanitize_dict_string_values(value) for key, value in value.items()}
    if isinstance(value, list):
      return [await self.__sanitize_dict_string_values(item) for item in value]
      
    return value.strip().strip('\'') if isinstance(value, str) else value

  async def build_flight_object(self, amount: float, url: str, departure_city: str, arrival_city: str, departure_companies: list[str], departure_leave_times: list[str], departure_arrival_times: list[str], departure_flight_durations: list[str], departure_stopovers: list[str], departure_aiport_iata: str, arrival_airport_iata: str, return_companies: list[str], return_leave_times: list[str], return_arrival_times: list[str], return_flight_durations: list[str], return_stopovers: list[str], return_departure_aiport_iata: str, return_arrival_airport_iata: str) -> FlightModel:
    return await self.__sanitize_dict_string_values({
      'amount': amount,
      'url': url,
      'itineraries': {
        'departure_city': departure_city,
        'arrival_city': arrival_city,
        'outbound': {
          'companies': departure_companies,
          'departure_times': departure_leave_times,
          'arrival_times': departure_arrival_times,
          'flight_durations': departure_flight_durations,
          'stopovers': departure_stopovers,
          'departure_airport_iata': departure_aiport_iata,
          'arrival_airport_iata': arrival_airport_iata
        },
        'inbound': {
          'companies': return_companies,
          'departure_times': return_leave_times,
          'arrival_times': return_arrival_times,
          'flight_durations': return_flight_durations,
          'stopovers': return_stopovers,
          'departure_airport_iata': return_departure_aiport_iata,
          'arrival_airport_iata': return_arrival_airport_iata
        }
      }
    })