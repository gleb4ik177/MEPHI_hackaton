import uvicorn
import pandas as pd
from fastapi import FastAPI
from fastapi import APIRouter
from api_for_tg.services import model_query as mq, clean_date, df_traffic
from cydifflib import get_close_matches


df = None
app = FastAPI()

#uvicorn.run(app, host="localhost", port=8080)
#router = APIRouter()
#app.include_router(router, prefix="/api/v1", tags=["ml/dl"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup():
    df = pd.read_excel('api_for_tg\data\stations.xlsx')



@app.get("/get_traffic")
async def get_traffic(query: str):
    df_query = mq(query)

    station = df_query['station']
    date = df_query['date']

    if station is None or date is None:
        return 'плохой запрос'
    
    df_query = clean_date(date)
    ds = df_query['date_start']
    de = df_query['date_end']
 
    if ds is None or de is None:
        return 'плохой запрос'
    
    ret = get_close_matches(station.lower(), df['Станция'], n=1)
    if len(ret) == 0:
        return 'плохой запрос'
    else:
        station = ret[0]
    
    
    traffic_number = df_traffic(station = station, start_date= ds, end_date= de, df = df)

    ret = {'traffic' : traffic_number, 'date_start' : ds, 'date_end' : de}
    
    return ret



