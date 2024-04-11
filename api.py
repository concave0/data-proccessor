from fastapi import FastAPI
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json

# Proccesses to schedule
class BatchProccess:
  def __init__(self) -> None:
    self.proccess = {}
# Storing proccess
batch_proccess = BatchProccess()
# Scheduler
process_scheduler = BackgroundScheduler()

# Proccess Data Schedulers
def proccess_batch_data_store():
  with open('data/batch_data.json', 'w') as data:
    info = json.load(data)
    info.update(batch_proccess.proccess)
    json.dump(info, data, indent=4)
    data.close()

def proccess_deletion_policy():
  with open('data/batch_data.json', '+w') as data:
    empty_data = {"data": "Filler data"}
    json.dump(empty_data, data, indent=4)
    data.close()

# Proccess data every hour
process_scheduler.add_job(proccess_batch_data_store, 'interval', seconds=3600)
# Delete data every 30 days 
process_scheduler.add_job(proccess_deletion_policy, 'interval', seconds=2592000)

# Setting up FastAPI
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
templates = Jinja2Templates(directory="templates")

""" Moisture Levels Data """
class MoistureLevelData:
  moisture_levels = {}
moisture_level_data = MoistureLevelData()

""" Regular Website Routes"""
@app.get("/", response_class=HTMLResponse)
@limiter.limit("1/second")
async def hello_world(request: Request):
  templates.TemplateResponse("hello.html", {"request": request})
  
""" Basic Endpoints to If Up"""
@app.get("/iam-up")
@limiter.limit("1/second")
async def ping_me(request: Request):
  return {"message": "I'm Alive"}

""" Endpoints """
@app.get("/store-water-moisture")
async def udpates_on_watering_status(request: Request):
  data = await request.json() 
  moisture = data.get("moisture_level") 
  current_datetime = datetime.now()
  moisture_level_data.moisture_levels[str(current_datetime)] = moisture

  with open("data/moisture_levels.json", 'r+') as data: 
    file_data = json.load(data)
    file_data.update(moisture)
    new_data = json.dump(file_data, data, indent=4)

  return {"Recorded": True}    
    
    
  


  
  
