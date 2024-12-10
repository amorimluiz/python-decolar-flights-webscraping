import telegram
import dotenv
import os
from models.flight_model import FlightModel
import re
import datetime

dotenv.load_dotenv()

class TelegramService:
  def __init__(self):
    token = os.getenv('DECOLAR_CRAWLER_TELEGRAM_BOT_TOKEN')
    self.__bot = telegram.Bot(token=token)
    self.__chat_id = os.getenv('DECOLAR_CRAWLER_TELEGRAM_CHAT_ID')
  
  def __make_card_buttons(self, flight: FlightModel) -> telegram.InlineKeyboardMarkup:
    return telegram.InlineKeyboardMarkup([
      [telegram.InlineKeyboardButton('Ver na Decolar', url=flight['url'])]
    ])

  def __build_message_card(self, flight: FlightModel) -> str:
    outbound_departure_airport_iata = flight['itineraries']['outbound']['departure_airport_iata']
    outbound_arrival_airport_iata = flight['itineraries']['outbound']['arrival_airport_iata']
    inbound_departure_airport_iata = flight['itineraries']['inbound']['departure_airport_iata']
    inbound_arrival_airport_iata = flight['itineraries']['inbound']['arrival_airport_iata']

    dates = re.match(r'.*\/(\d{4}-\d{2}-\d{2}\/\d{4}-\d{2}-\d{2}).*', flight['url']).group(1).split('/')
    dates = [datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y') for date in dates]

    return f'''
    *✈️ Detalhes do Voo ✈️* 
    *Rota*: 🌍 {flight["itineraries"]["departure_city"]} → {flight["itineraries"]["arrival_city"]}
    *Valor*: 💰 {f'{flight['amount']:.2f}'.replace('.', ',')}
    *Datas*: 📅 {dates[0]} → {dates[1]}
    *Aeroportos*: 🛫 {outbound_departure_airport_iata} → {outbound_arrival_airport_iata} / {inbound_departure_airport_iata} → {inbound_arrival_airport_iata} 🛬 
    *Companhias*: 🛩️ {', '.join(set(flight['itineraries']['outbound']['companies']))} / {', '.join(set(flight['itineraries']['inbound']['companies']))}
    '''
  
  async def send_flight_message(self, flight: FlightModel) -> None:
    message = self.__build_message_card(flight)

    buttons = self.__make_card_buttons(flight)

    async with self.__bot:
      await self.__bot.send_message(chat_id=self.__chat_id, text=message, parse_mode='MarkdownV2', reply_markup=buttons)
    