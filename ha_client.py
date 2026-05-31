import os
from dotenv import load_dotenv
import requests
from dataclasses import dataclass

@dataclass
class EntityState:
    state: str
    attributes: dict
    last_changed:str
    error:str 

load_dotenv()

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

def get_state(entity):
    url = f"{HA_URL}/api/states/{entity}"
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}

    try: 
        response = requests.get(url, headers=headers)   
        result = response.json()
        if(response.status_code == 200):
            return EntityState(
                state=result["state"],
                attributes=result["attributes"],
                last_changed=result["last_changed"],
                error=None
            )
        else:
            return EntityState(
                state=None,
                attributes=None,
                last_changed=None,
                error=result["message"]
        )
    except Exception as e: 
        return EntityState(
            state=None,
            attributes=None,
            last_changed=None,
            error=e
        )


def run_action(entity):
    url = f"{HA_URL}/api/services/button/press"
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}

    try:
        response = requests.post(url, json={"entity_id": entity}, headers=headers)
        result = response.json()
        if(response.status_code == 200):
            return result[0]["state"]
        else:
            return result[0]["message"]
    except Exception as e:
        return e
    
def check_health():
    url = f"{HA_URL}/api/"
    headers = {"Authorization": f"Bearer {HA_TOKEN}"}

    try: 
        response = requests.get(url, headers=headers)   
        result = response.json()
        return result['message']
    except Exception as e: 
        return e