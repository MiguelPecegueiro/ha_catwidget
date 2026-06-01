from PySide6 import QtCore
from ha_client import get_state, check_health, run_action
import json

class Worker(QtCore.QThread):
    data_ready = QtCore.Signal(object)

    def run(self):
        litterboxbinapi_object = get_state('automation.catlink_bin_is_full')
        litterboxcleaningapi_object = get_state('automation.catlink_stops_cleaning')
        apistatusapi_object = check_health()

        apiresults = {
            "litterboxbin": litterboxbinapi_object, 
            "litterboxcleaning": litterboxcleaningapi_object,
            "apistatus": apistatusapi_object
        }

        with open("config.json", "r", encoding= "utf-8") as f:
            config = json.load(f)
        
        for cat in config["cats"]:
            apiresults[f'{cat["name"]}foodstatus'] = get_state(f'binary_sensor.one_rfid_smart_feeder_{cat["name"]}_food_status')
            apiresults[f'{cat["name"]}lastfeedtime'] = get_state(f'sensor.one_rfid_smart_feeder_{cat["name"]}_last_feed_time')
            apiresults[f'{cat["name"]}feedingtimes'] = get_state(f'sensor.one_rfid_smart_feeder_{cat["name"]}_today_s_feeding_times')

        self.data_ready.emit(apiresults)
