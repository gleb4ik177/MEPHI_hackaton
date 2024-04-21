import json
from llamaapi import LlamaAPI
import re
import datetime as dt
import dateutil.relativedelta as relativedelta
import pandas as pd
from datetime import timedelta
import os
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt
from pandas.plotting import table
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def model_query(query : str):
    ret = {'station' : None, 'date' : None}

    llama = LlamaAPI("LL-JAS1EJsZRdhCwIonyLuBxJN09FkIb9w67y99HCTE1OAVlSn4z9On80hpO6djvKkm")
    api_request_json = {
    "messages": [
        {"role": "user", "content": 'пассажиропоток ' + query.lower()},
    ],
    "functions": [
        {
            "name": "get_station_and_date",
            "description": "Представь, что ты сотрудник справочной станции метро Москвы. Сегодня 3 апреля. Ты должен вычленять название станции метро и дату из запроса.",
            "parameters": {
                "type": "object",
                "properties": {
                    "station": {
                        "type": "string",
                        "description": "Название станции московского метро в формате Название станции на русском языке, например Арбатская",
                    },
                    "date": {
                        "type": "string",
                        "description": "Дата упомянутая пользователем. Если пользователь ввел относительную дату такую как: через 3 дня, спустя неделю, завтра, через день или неделю назад, то просто выведи относительную дату, которую он ввел." +\
                         "Если пользователь не указал год, то верни результат в формате 2024 - месяц - день, например 2024-02-11." +\
                         "Если пользователь ввел одну дату то выведи ее в формате год-месяц-день, например 2024-03-13." +\
                         "Если пользователь ввел временной промежуток, то верни его в формате 'год-месяц-день - год-месяц-день', например 2024-03-03 - 2024-05-30."
                    }
                },
            },
            "required": ["station", "date"],
        }
        ],
        "stream": False,
        "function_call": "get_station_and_date",
    }

    try:
        response = llama.run(api_request_json)
        r = response.json()
        ans = re.findall('{.*}', str(r['choices'][0]['message']['function_call']['arguments']))[0]
        ans = eval(ans)
        ret['station'] = ans['station']
        ret['date'] = ans['date']
        print(ret)
        return ret
    except:
        return ret
    

def clean_date(date : str):
    ret = {'date_start' : None, 'date_end' : None}
    date = str(date)

    mon = {'январ' : '01', 'февраля': '02', 'марта' : '03', 'апреля' : '04', 'мая' : '05', 'июня' : '06', 'January' : '01', 'February' : '02', 'March' : '03', 'April' : '04', 'May' : '05', 'June' : '06'}

    if ' - ' in date:
        d = date.split(' - ')
        d1 = d[0]
        d2 = d[1]

        if re.match(r'^\d{2}-\d{2}-\d{4}$', d1) is not None:
            d1 = d1[6:] + d1[2:6] + d1[:2]   
        if re.match(r'^\d{2}-\d{2}-\d{4}$', d2) is not None:
            d2 = d2[6:] + d2[2:6] + d2[:2] 
            
        try:
            n1 = re.findall(r"^\d+\s", d1)[0]
            n1 = n1[:-1]
            n2 = re.findall(r"^\d+\s", d2)[0]
            n2 = n2[:-1]

            for key, value in mon.items():

                if key in d1:
                    d1 = '2024-' + value + '-'
                    if int(n1) < 10:
                        d1 += '0' + n1
                    else:
                        d1 += n1

                if key in d2:
                    d2 = '2024-' + value + '-'
                    if int(n2) < 10:
                        d2 += '0' + n2
                    else:
                        d2 += n2    
        except:
            pass
        ret['date_start'] = d1
        ret['date_end'] = d2
        print(ret)
        return ret    
    
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date) is not None:
        ret['date_end'] = date
        ret['date_start'] = date
        return ret
    
    if re.match(r'^\d{2}-\d{2}-\d{4}$', date) is not None:
        d = date[6:] + date[2:6] + date[:2]
        ret['date_end'] = d
        ret['date_start'] = d
        return ret
    
    if '-' in date:
        try:
            n1 = re.findall(r"\d+\s", date)[0]
            n1 = n1[:-1]
            n2 = re.findall(r"\d+\s", date)[1]
            n2 = n2[:-1]

            for key, value in date:
                if key in date:
                    d1 = '2024-' + value
                    d2 = '2024-' + value
                    if n1 < 10:
                        d1 += '0' + n1
                    else:
                        d1 += n1   

                    if n2 < 10:
                        d2 += '0' + n2
                    else:
                        d2 += n2

                    ret['date_start'] = d1
                    ret['date_end'] = d2
                    print(ret)
                    return ret
        except:
            pass

    today = dt.datetime.strptime('2024-04-03', "%Y-%m-%d")

    flag = 1
    rd = relativedelta.relativedelta(days = 1)  

    if 'вчера'in date:
        rd = relativedelta.relativedelta(days = 1) 
        flag = -1 

    if 'позавчера' in date:
        rd = relativedelta.relativedelta(days = 2)
        flag = -1

    if 'назад' in date or 'ago' in date or 'last' in date:
        flag = -1

    n = re.findall(r'^\d+\s', date)
    if len(n) > 0:
        n = int(n[0][:-1])
    else:
        n = 1    

    if 'week' in date or 'недел' in date:  
        rd = relativedelta.relativedelta(weeks = n)

    elif 'ден' in date or 'day' in date or 'дн' in date:
        if 'сегодня' in date or 'today' in date:
            n = 0
        rd = relativedelta.relativedelta(days = n)  

    elif 'tommorow' in date or 'завтра' in date:
        if 'after' in date or 'после' in date:
            n = 2
        else:
            n = 1
        rd = relativedelta.relativedelta(days = n)     

    elif 'месяц' in date or 'month' in date:
        rd = relativedelta.relativedelta(months = n)

    if flag > 0:        
        d = today + rd
    else:
        d = today - rd
    
    single_date = d.strftime('%Y-%m-%d')   
    ret['date_end'] = single_date
    ret['date_start'] = single_date

    return ret


def df_traffic(station:str, start_date:str, end_date:str, df:pd.DataFrame):
  today = dt.datetime.strptime('2024-04-03', "%Y-%m-%d")
  end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
  start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
  df = (df[df['Станция']==station].drop(columns=['Дата','Номер линии','Станция']).T)
  df = df[[df.columns[0]]]
  df = df.rename(columns={df.columns[0]:'stream'})
  df['date'] = df.index
  df.reset_index(drop=True,inplace=True)
  df.stream = df.stream[::-1].reset_index(drop=True)
  df.date = df.date[::-1].reset_index(drop=True)
  #df.date = df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
  if today >= end_date:
    df = df[df.date.between(start_date,end_date)]
    if df.shape[0] >= 10:
        plt.figure(figsize=(8, 6), dpi=80)
        plt.plot(df[df.date<=today].date,df[df.date<=today].stream) 
        plt.plot(df[df.date>=today].date,df[df.date>=today].stream,color='r') 
        plt.xticks(df.date, rotation ='horizontal') 
        plt.locator_params(axis='x', nbins=4)
        if end_date > today and start_date < today:
            plt.axvline(x=today,color='r',linestyle='--')
        plt.ylabel('traffic')
        plt.xlabel('date')
        try:
            os.remove('graph.png')
        except:
            pass    
        plt.savefig('graph.png')
    df.date = df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
    return df
  fitted_model = ExponentialSmoothing(df['stream'],trend='mul',seasonal='add',seasonal_periods=30).fit()
  full_df = pd.DataFrame()
  part_df = pd.DataFrame() 
  if start_date <= today:
    part_df = df[df.date.between(start_date,today)]
  fitted_model = ExponentialSmoothing(df['stream'],trend='mul',seasonal='add',seasonal_periods=30).fit()
  full_df['stream'] = fitted_model.forecast((end_date - today).days).rename('stream')
  full_df['date'] = pd.date_range(today + timedelta(days=1),end_date)
  full_df = pd.concat([part_df, full_df])
  if start_date > today:
    full_df = full_df[full_df.date.between(start_date,end_date)]
  if full_df.shape[0] >= 10:
    plt.figure(figsize=(8, 6), dpi=80)
    plt.plot(full_df[full_df.date<=today].date,full_df[full_df.date<=today].stream) 
    plt.plot(full_df[full_df.date>=today].date,full_df[full_df.date>=today].stream,color='r') 
    plt.xticks(full_df.date, rotation ='horizontal') 
    plt.locator_params(axis='x', nbins=4)
    if end_date > today and start_date < today:
      plt.axvline(x=today,color='r',linestyle='--')
    plt.ylabel('traffic')
    plt.xlabel('date')
    try:
        os.remove('graph.png')
    except:
        pass
    plt.savefig('graph.png')
  full_df.date = full_df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
  full_df.reset_index(drop=True,inplace=True)
  return full_df
