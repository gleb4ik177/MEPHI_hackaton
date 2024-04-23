import telebot
import os
from telebot import types
from tg_services import model_query as mq, clean_date, df_traffic
import pandas as pd
import datetime as dt
from cydifflib import get_close_matches

df = pd.read_excel('tg_bot\data\stations.xlsx')
bot = telebot.TeleBot(TG_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def startBot(message):
  first_mess = f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!\nРекоммендуем вводить даты в запроса в одном из следующих форматов:\nчисло - месяц\nс число - месяц по число - месяц\nпериод назад либо спустя период\nтакже, пожалуйста пишите правильно"
  bot.send_message(message.chat.id, first_mess, parse_mode='html')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
  all_good = True
  ret = {'traffic' : None, 'date_start' : None, 'date_end' : None}
  df_query = mq(message.text)

  station = df_query['station']
  date = df_query['date']

  if station is None or date is None:
      print('плохой запрос плохая станция или дата')
      all_good = False
  
  if all_good:
    df_query = clean_date(date)
    ds = df_query['date_start']
    de = df_query['date_end']

    if ds is None or de is None:
      print('плохой запрос плохая дата')
      all_good = False
  
  #print(station)
  #print(date)
  if all_good:
    ret = get_close_matches(station.lower(), df['Станция'], n=1)
    if len(ret) == 0:
      print('лохой запрос')
      all_good = False
    else:
      station = ret[0]
  
  if all_good:
    print(ds)
    print(de)
    traffic_number = df_traffic(station = station, start_date= ds, end_date= de, df = df)
  
  if not all_good:
     bot.send_message(message.chat.id, 'модель не распознала запрос')
  else:   
    if dt.datetime.strptime(de, "%Y-%m-%d") < dt.datetime.strptime('2024-01-01', '%Y-%m-%d'):
      bot.send_message(message.chat.id, 'по данной дате информации нет')
    else:  
      bot.send_message(message.chat.id, f"<u>СТАНЦИЯ:</u> {station}\n" +\
                                        f"<u>ИНТЕРВАЛ:</u> {ds} - {de}\n" +\
                                        f"<u>СУММА:</u> {round(traffic_number.stream.sum())}\n" +\
                                        f"<u>МИН:</u> {round(traffic_number.stream.min())}\n" +\
                                        f"<u>МАКС:</u> {round(traffic_number.stream.max())}\n" +\
                                        f"<u>СРЕД:</u> {round(traffic_number.stream.mean())}\n",parse_mode='html')
      if len(traffic_number) >= 10:
        img = open('graph.png', 'rb')
        bot.send_photo(message.chat.id, img)
      else:
        s = ""
        s+=("DATE            | TRAFFIC\n")
        for i in traffic_number.index:
          s+=(str(traffic_number.date[i])+" | "+str(round(traffic_number.stream[i])).rjust(7)+"\n")
        bot.send_message(message.chat.id, s)
bot.infinity_polling()