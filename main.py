from file_io.file_io import FileIO
from scraper.decolar_scraper import DecolarScraper
from models.scrape_params_model import ScrapeParamsModel
from services.telegram_service import TelegramService
import asyncio
import time
import dotenv
import os

dotenv.load_dotenv()

scrape_params_file_name = 'scrape_params.json'

async def build_scrape_url(scrape_data: ScrapeParamsModel) -> str:
  return f"https://www.decolar.com/shop/flights/results/roundtrip/{scrape_data['departure_airport_iata']}/{scrape_data['return_airport_iata']}/{scrape_data['departure_date']}/{scrape_data['return_date']}/1/0/0?from=SB&di=1&reSearch=true"

async def build_scrape_urls(to_scrape_list: list[ScrapeParamsModel]) -> list[str]:
  tasks = [build_scrape_url(scrape_data) for scrape_data in to_scrape_list]
  return await asyncio.gather(*tasks)
  
def main():
  scrape_params_file = FileIO(scrape_params_file_name)

  if not scrape_params_file.exists():
    print('Scrape params file not found')
    return

  scrape_params = scrape_params_file.read_json_file()
  scrape_urls = asyncio.run(build_scrape_urls(scrape_params))

  scraper = DecolarScraper(scrape_urls)
  flights = asyncio.run(scraper.scrape([float(scrape_param['maximum_price']) for scrape_param in scrape_params]))

  telegram_service = TelegramService()

  for flight in flights:
    asyncio.run(telegram_service.send_flight_message(flight))


if __name__ == "__main__":
  hours_in_seconds = 60 * 60
  while True:
    scrape_interval_hours = int(os.getenv('SCRAPE_INTERVAL_HOURS'))
    sleep_time = scrape_interval_hours * hours_in_seconds
    print(f'Scraping at {time.ctime()}')
    main()
    time.sleep(sleep_time)