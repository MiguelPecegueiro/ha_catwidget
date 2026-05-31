import sys
import json
import win32gui
import ctypes
from datetime import datetime, timezone
import math
from PySide6 import QtCore, QtWidgets, QtGui
from ha_client import get_state, check_health, run_action
from utils import format_time_ago

class CatCard(QtWidgets.QFrame):
    def __init__(self,cat):
        super().__init__()

        self.cat_name = cat;

        self.setStyleSheet("""
            QFrame { background-color: #1e1e2e; border-radius: 12px; border: 1px solid #2a2a3e; }
            QLabel { border: none; background: transparent; color: #dfe6e9; }
            QPushButton { border: 1px solid #3a3a5e; border-radius: 6px; background: transparent; color: #dfe6e9; padding: 4px; }
            QPushButton:hover { background: #2a2a4e; }
        """)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.topcard_layout = QtWidgets.QHBoxLayout()
        self.cat_label = QtWidgets.QLabel(cat)
        self.topcard_layout.addWidget(self.cat_label) 
        self.cat_photo = QtWidgets.QLabel('photocat') 
        self.topcard_layout.addWidget(self.cat_photo) 
        self.main_layout.addLayout(self.topcard_layout)


        self.foodstatus_line = QtWidgets.QHBoxLayout()
        self.foodstatus_label = QtWidgets.QLabel('Food level:')
        self.foodstatus_line.addWidget(self.foodstatus_label)
        self.foodstatus_line_statuscard = QtWidgets.QHBoxLayout()     
        self.foodstatus_state = QtWidgets.QLabel('Unknown')       
        self.foodstatus_line_statuscard.addWidget(self.foodstatus_state)
        self.foodstatus_stateindicator = QtWidgets.QLabel('●')       
        self.foodstatus_stateindicator.setStyleSheet(f'font-size: 20px; color: #888780')
        self.foodstatus_line_statuscard.addWidget(self.foodstatus_stateindicator)           
        self.foodstatus_line.addLayout(self.foodstatus_line_statuscard)
        self.main_layout.addLayout(self.foodstatus_line)


        self.lastfeedtime_line = QtWidgets.QHBoxLayout()
        self.lastfeedtime_label = QtWidgets.QLabel('Last feed time:')
        self.lastfeedtime_line.addWidget(self.lastfeedtime_label)
        self.lastfeedtime_state = QtWidgets.QLabel('Unknown')       
        self.lastfeedtime_line.addWidget(self.lastfeedtime_state)
        self.main_layout.addLayout(self.lastfeedtime_line)

        self.todayfeedingtime_line = QtWidgets.QHBoxLayout()
        self.todayfeedingtime_label = QtWidgets.QLabel('Today feed count:')
        self.todayfeedingtime_line.addWidget(self.todayfeedingtime_label)
        self.todayfeedingtime_state = QtWidgets.QLabel('Unknown')       
        self.todayfeedingtime_line.addWidget(self.todayfeedingtime_state)
        self.main_layout.addLayout(self.todayfeedingtime_line)
    

        self.feedcat_button = QtWidgets.QPushButton(f'Feed {cat}')
        self.main_layout.addWidget(self.feedcat_button)

        self.feedcat_label = QtWidgets.QLabel('')
        self.main_layout.addWidget(self.feedcat_label)

        self.feedcat_button.clicked.connect(lambda: self.feedcat(cat))

        self.update_status(cat)  

    def update_status(self,cat):

        foodstatus_api = get_state(f'binary_sensor.one_rfid_smart_feeder_{cat}_food_status')
        foodstatus = foodstatus_api.state
        foodstatusindicator = '#fdcb6e'
        if(foodstatus == None):
            foodstatus = foodstatus_api.error
        else:           
            if(foodstatus == 'off'):
                foodstatus = 'OK'
                foodstatusindicator = '#00b894'
            if(foodstatus == 'on'):
                foodstatus = 'Empty!'   
                foodstatusindicator = '#E24B4A'              
        self.foodstatus_state.setText(foodstatus)    
        self.foodstatus_stateindicator.setStyleSheet(f'font-size: 20px; color: {foodstatusindicator}')


        lastfeedtime_api = get_state(f'sensor.one_rfid_smart_feeder_{cat}_last_feed_time')
        lastfeedtime = lastfeedtime_api.state
        if(lastfeedtime == None):
            lastfeedtime = lastfeedtime_api.error
        else:  
            lastfeedtime = format_time_ago(lastfeedtime)                       
        self.lastfeedtime_state.setText(str(lastfeedtime))


        todayfeedingtime_api = get_state(f'sensor.one_rfid_smart_feeder_{cat}_today_s_feeding_times')
        todayfeedingtime = todayfeedingtime_api.state
        if(todayfeedingtime == None):
            todayfeedingtime = todayfeedingtime_api.error
        self.todayfeedingtime_state.setText(f'{todayfeedingtime} times today')

    @QtCore.Slot()
    def feedcat(self,cat):
        self.feedcat_label.setText(str(run_action(f'button.one_rfid_smart_feeder_{cat}_manual_feed')))



class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setStyleSheet("""
            QWidget { background-color: #0f0f0f; color: #dfe6e9; }
            QPushButton { border: 1px solid #3a3a5e; border-radius: 6px; background: transparent; color: #dfe6e9; padding: 6px; }
            QPushButton:hover { background: #1e1e2e; }
        """)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 10)

        self.topstatus_layout = QtWidgets.QHBoxLayout()
        self.topstatus_layout.setSpacing(10)
        self.topstatus_layout.setContentsMargins(10, 10, 10, 10)

        self.litterboxbinstatus_indicator = QtWidgets.QLabel('●')
        self.litterboxbinstatus_indicator.setStyleSheet("font-size: 50px; color: #888780;")
        self.litterboxbinstatus_indicator.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.topstatus_layout.addWidget(self.litterboxbinstatus_indicator)   
        self.litterboxbinstatus_statuscard_label = QtWidgets.QLabel('Litter Box Bin\nUnknown\nUnknown')
        self.topstatus_layout.addWidget(self.litterboxbinstatus_statuscard_label)

        self.litterboxcleaningstatus_indicator = QtWidgets.QLabel('●')
        self.litterboxcleaningstatus_indicator.setStyleSheet("font-size: 50px; color: #888780;")
        self.litterboxcleaningstatus_indicator.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.topstatus_layout.addWidget(self.litterboxcleaningstatus_indicator)
        self.litterboxcleaningstatus_statuscard_label = QtWidgets.QLabel('Litter Box Cleaning\nUnknown\nUnknown')
        self.topstatus_layout.addWidget(self.litterboxcleaningstatus_statuscard_label)


        self.apistatus_indicator = QtWidgets.QLabel('●')
        self.apistatus_indicator.setStyleSheet("font-size: 50px; color: #888780;")
        self.apistatus_indicator.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.topstatus_layout.addWidget(self.apistatus_indicator)
        self.apistatus_statuscard_label = QtWidgets.QLabel('API\nUnknown\nUnknown')    
        self.topstatus_layout.addWidget(self.apistatus_statuscard_label)
       
        self.main_layout.addLayout(self.topstatus_layout)


        self.catcards_layout = QtWidgets.QHBoxLayout()

        with open("config.json", "r", encoding= "utf-8") as f:
            config = json.load(f)
        
        self.cat_cards=[]
        for cat in config["cats"]:
            card = CatCard(cat)
            self.cat_cards.append(card)
            self.catcards_layout.addWidget(card)

        self.main_layout.addLayout(self.catcards_layout)



        self.button = QtWidgets.QPushButton("Feed all cats")
        self.main_layout.addWidget(self.button)
        
        self.button.clicked.connect(self.feedcats)

        self.update_status()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(60000)
        

    def update_status(self):
        litterboxbinstatus_api = get_state('automation.catlink_bin_is_full')
        litterboxbinstatus = litterboxbinstatus_api.state
        litterboxbinstatusindicator = '#fdcb6e'
        if(litterboxbinstatus == None):
            litterboxbinstatus = litterboxbinstatus_api.error
        else:       
            if(litterboxbinstatus == "on"):
                litterboxbinstatus = "Full!"
                litterboxbinstatusindicator = '#E24B4A'                
            if(litterboxbinstatus == "off"):
                litterboxbinstatus = "OK"
                litterboxbinstatusindicator = '#00b894'                             
        self.litterboxbinstatus_statuscard_label.setText(f'Litter Box Bin\n{litterboxbinstatus}\n{format_time_ago(litterboxbinstatus_api.last_changed)}')
        self.litterboxbinstatus_indicator.setStyleSheet(f'font-size: 50px; color: {litterboxbinstatusindicator}')


        litterboxcleaningstatus_api = get_state('automation.catlink_stops_cleaning')
        litterboxcleaningstatus = litterboxcleaningstatus_api.state
        litterboxcleaningstatusindicator = '#fdcb6e'
        if(litterboxcleaningstatus == None):
            litterboxcleaningstatus = litterboxcleaningstatus_api.error
        else:
            if(litterboxcleaningstatus == "on"):
                litterboxcleaningstatus = "Stopped!"
                litterboxcleaningstatusindicator = "#E24B4A"
            if(litterboxcleaningstatus == "off"):
                litterboxcleaningstatus = "OK"
                litterboxcleaningstatusindicator = "#00b894"
        self.litterboxcleaningstatus_statuscard_label.setText(f'Litter Box Cleaning\n{litterboxcleaningstatus}\n{format_time_ago(litterboxcleaningstatus_api.last_changed)}')       
        self.litterboxcleaningstatus_indicator.setStyleSheet(f'font-size: 50px; color: {litterboxcleaningstatusindicator}')


        
        apistatus = check_health()
        apistatusindicator = '#E24B4A'

        self.apistatus_statuscard_label.setText(f'API Status\n{apistatus}\n{datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")}')
        if(apistatus == 'API running.'):
            apistatusindicator = '#00b894'
        self.apistatus_indicator.setStyleSheet(f'font-size: 50px; color: {apistatusindicator}')

        for card in self.cat_cards:
            card.update_status(card.cat_name)


        

    @QtCore.Slot()
    def feedcats(self):        
        for card in self.cat_cards:
            card.feedcat(card.cat_name)
      


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
    widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
    
    hwnd = int(widget.winId())
    progman = win32gui.FindWindow("Progman",None)
    ctypes.windll.user32.SendMessageTimeoutW(progman,0x052c,0,0,0,1000,None)

    workerw = None
    def enum_windows_callback(hwnd, _):
        global workerw
        shell = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
        print(f"hwnd: {hwnd}, shell: {shell}")
        if shell:
            workerw = hwnd #win32gui.FindWindowEx(None, hwnd, "WorkerW", None)
            print(f"Found! workerw: {workerw}")
        return True

    win32gui.EnumWindows(enum_windows_callback,None)

    if workerw:
        win32gui.SetParent(hwnd,workerw)

    print(f"workerw: {workerw}")
    print(f"hwnd: {hwnd}")
    widget.show()
    widget.raise_()
    sys.exit(app.exec())




