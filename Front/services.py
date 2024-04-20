import json
from llamaapi import LlamaAPI
import re
import datetime as dt
import dateutil.relativedelta as relativedelta
import pandas as pd
from datetime import timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def model_query(query : str):
    ret = {'station' : None, 'date' : None}

    llama = LlamaAPI("LL-JAS1EJsZRdhCwIonyLuBxJN09FkIb9w67y99HCTE1OAVlSn4z9On80hpO6djvKkm")
    api_request_json = {
    "messages": [
        {"role": "user", "content": query},
    ],
    "functions": [
        {
            "name": "get_station_and_date",
            "description": "Ты сотрудник справочной станции метро Москвы. Сегодня 20 апреля 2024. В запросе пользователя ты должен вычленять название станции метро и дату.",
            "parameters": {
                "type": "object",
                "properties": {
                    "station": {
                        "type": "string",
                        "description": "Название станции московского метро в формате Название станции, например Арбатская",
                    },
                    "date": {
                        "type": "string",
                        "description": "Дата упомянутая пользователем. Если пользователь ввел одну дату, то выведи ее в формате 'год-месяц-день', например '2024-04-03'." + \
                         "Если пользователь ввел временной промежуток, то верни его в формате 'год-месяц-день - год-месяц-день', например '2024-03-03 - 2024-04-02'."
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
    except:
        return ret
    
    ans = re.findall('{.*}', str(r['choices'][0]['message']['function_call']['arguments']))[0]

    try:
        ans = eval(ans)
        ret['station'] = ans['station']
        ret['date'] = ans['date']
        return ret
    except:
        return ret
    

def clean_date(date : str):
    ret = {'date_start' : None, 'date_end' : None}

    n = re.findall(r'^\d+', date)[0]

    if ' - ' in date:
        d = date.split(' - ')
        d1 = d[0]
        d2 = d[1]

        ret['date_start'] = d1
        ret['date_end'] = d2

        return ret
    
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date) is not None:
        ret['date_end'] = date
        ret['date_start'] = date
        return ret
    
    today = dt.datetime(year = 2024, month = 4, day = 3)

    if 'вчера'in date:
        rd = relativedelta.relativedelta(day = 2)  

    if 'позавчера' in date:
        rd = relativedelta.relativedelta(day = 1)

    if 'назад' in date or 'ago' in date:
        n = re.findall(r'^\d+', date)[0]
        n = int(n)

    if 'week' or 'недел' in date:  
        rd = relativedelta.relativedelta(weeks = n)

    if 'ден' or 'day' or 'дн' in date:
        rd = relativedelta.relativedelta(day = n)

    if 'месяц' or 'month' in date:
        rd = relativedelta.relativedelta(months = n)

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
        full_df = full_df[full_df.date.between(start_date,end_date)].reset_index(drop=True)
    full_df.date = full_df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
    return full_df.stream.sum()

def get_closest_station(station, df):
    


