import math
from datetime import datetime, timezone

def format_time_ago(inputdate):
    try:
        inputdate =  datetime.fromisoformat(inputdate)           
        howlongago = datetime.now(timezone.utc) - inputdate
        if(howlongago.days > 0):
            return f'{math.floor(howlongago.days)} day(s) ago at {inputdate.strftime("%H:%M")}'
        elif(howlongago.total_seconds()>=3600):
           return f'{math.floor(howlongago.total_seconds()/3600)} hour(s) ago'
        elif(howlongago.total_seconds()>=60):
            return f'{math.floor(howlongago.total_seconds()/60)} minute(s) ago'
        else:
            return f'{math.floor(howlongago.total_seconds())} second(s) ago'
    except Exception as e:
        return e                