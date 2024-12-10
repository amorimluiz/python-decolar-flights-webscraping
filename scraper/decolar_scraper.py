from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, ResultSet
from random import randint
from models.flight_model import FlightModel
from models.itinerary_model import ItineraryModel
from services.flight_service import FlightService
import asyncio
import time

class DecolarScraper:
  def __init__(self, urls: list[str]):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    self.__options = webdriver.ChromeOptions()
    self.__options.add_argument(f'user-agent={user_agent}')
    self.__options.add_argument('--headless=new')
    self.__options.add_argument('--disable-blink-features=AutomationControlled')
    self.__options.add_argument('--window-size=1000,600')
    self.__options.add_argument('--disable-gpu')
    self.__options.add_argument('--lang=pt-BR')
    self.__urls = urls
    self.__flight_service = FlightService()

  def __wait_for_element(self, driver: webdriver.Chrome, element: str, by: str, timeout: int) -> None:
    try:
      WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, element))
      )
    except Exception:
      raise Exception('Timeout waiting for element')

  def __extract_flight_amount(self, flight_container: BeautifulSoup) -> float:
    amount_container = flight_container.find('span', {'class': 'item-fare fare-price'})
    amount_soup = amount_container.find('span', {'class': 'price-amount'})
    return float(amount_soup.text.replace('.', '')) if amount_soup else None

  def __extract_city_by_container_class(self, container: BeautifulSoup, class_name: str) -> str:
    return container.find('span', {'class': class_name}).find('span', recursive=True).text
  
  def __extract_aiport_iata_by_container_class(self, container: BeautifulSoup, class_name: str) -> str:
    return container.find('span', {'class': class_name}).find('span', {'tooltip-class': 'popup-airport'}).text
  
  def __extract_nested_text_list_by_classes(self, container: BeautifulSoup, element_name: str, nested_element_name: str, class_name: str, nested_class_name: str) -> list[str]:
    soups: list[BeautifulSoup] = container.find_all(element_name, {'class': class_name})
    return [soup.find(nested_element_name, {'class': nested_class_name}).text for soup in soups]
  
  def __extract_list_text_by_class(self, container: BeautifulSoup, element_name: str, class_name: str) -> list[str]:
    return [soup.text for soup in container.find_all(element_name, {'class': class_name})]
  
  def __extract_flight_durations(self, container: BeautifulSoup) -> list[str]:
    durations_soups: list[BeautifulSoup] = container.find_all('span', {'class': 'duration-item-container -eva-3-tc-gray-2'})
    return [duration_soup.find('span').text for duration_soup in durations_soups]
  
  def __extract_itinerary_data(self, itinerary_container: BeautifulSoup) -> ItineraryModel:
    departure_airport_iata = self.__extract_aiport_iata_by_container_class(itinerary_container, 'route-location route-departure-location')
    arrival_airport_iata = self.__extract_aiport_iata_by_container_class(itinerary_container, 'route-location route-arrival-location')
    companies = self.__extract_nested_text_list_by_classes(itinerary_container, 'span', 'span', 'airline-container airline-logo-name-container -have-name', 'name')
    departure_times = self.__extract_nested_text_list_by_classes(itinerary_container, 'itinerary-element', 'span', 'leave', 'hour')
    arrival_times = self.__extract_nested_text_list_by_classes(itinerary_container, 'itinerary-element', 'span', 'arrive', 'hour')
    flight_durations = self.__extract_flight_durations(itinerary_container)
    stopovers = self.__extract_list_text_by_class(itinerary_container, 'span', 'stops-text')

    return {
      'companies': companies,
      'departure_times': departure_times,
      'arrival_times': arrival_times,
      'flight_durations': flight_durations,
      'stopovers': stopovers,
      'departure_airport_iata': departure_airport_iata,
      'arrival_airport_iata': arrival_airport_iata
    }

  async def __extract_flight_data(self, url: str, flight_container: BeautifulSoup, maximum_price: float) -> FlightModel | None:
    amount = self.__extract_flight_amount(flight_container)

    if (amount and amount > maximum_price):
      return None

    itineraries_container = flight_container.find('div', {'class': 'itineraries-container border-top-complete'})

    departure_city = self.__extract_city_by_container_class(itineraries_container, 'city-departure route-info-item route-info-item-city-departure')
    arrival_city = self.__extract_city_by_container_class(itineraries_container, 'city-arrival route-info-item route-info-item-city-arrival')

    departure_itinerary = itineraries_container.find('span', {'class': 'sub-cluster'})
    
    departure_itinerary_data = self.__extract_itinerary_data(departure_itinerary)

    return_itinerary = itineraries_container.find('span', {'class': 'sub-cluster last'})

    return_itinerary_data = self.__extract_itinerary_data(return_itinerary)

    return await self.__flight_service.build_flight_object(
      amount,
      url,
      departure_city,
      arrival_city,
      departure_itinerary_data['companies'],
      departure_itinerary_data['departure_times'],
      departure_itinerary_data['arrival_times'],
      departure_itinerary_data['flight_durations'],
      departure_itinerary_data['stopovers'],
      departure_itinerary_data['departure_airport_iata'],
      departure_itinerary_data['arrival_airport_iata'],
      return_itinerary_data['companies'],
      return_itinerary_data['departure_times'],
      return_itinerary_data['arrival_times'],
      return_itinerary_data['flight_durations'],
      return_itinerary_data['stopovers'],
      return_itinerary_data['departure_airport_iata'],
      return_itinerary_data['arrival_airport_iata']
    )

  async def scrape(self, maximum_prices: list[float]) -> list[FlightModel]:
    flights = []

    for index, url in enumerate(self.__urls):
      driver = webdriver.Chrome(options=self.__options)

      try:
        driver.get(url)
        self.__wait_for_element(driver, 'cluster-container', By.CLASS_NAME, randint(10, 15))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        driver.quit()
        time.sleep(randint(1, 10))

        flight_containers: ResultSet[BeautifulSoup] = soup.find_all('div', {'class': 'cluster-container'})
        tasks = [self.__extract_flight_data(url, flight_container, maximum_prices[index]) for flight_container in flight_containers]
        flights.extend([flight for flight in await asyncio.gather(*tasks) if flight])
      except Exception as e:
        driver.quit()
        print(f'Error scraping {url}\n{e}')

    return flights