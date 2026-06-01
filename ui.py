import sys
import json
from datetime import datetime, timezone
from PySide6 import QtCore, QtWidgets, QtGui
from ha_client import get_state, check_health, run_action
from utils import format_time_ago
from worker import Worker
import winreg
import os

class CatCard(QtWidgets.QFrame):
    def __init__(self,cat,catimg):
        super().__init__()
        
        self.cat_name = cat

        self.setStyleSheet("""
            QFrame { background-color: #1e1e2e; border-radius: 12px; border: 1px solid #2a2a3e; }
            QLabel { border: none; background: transparent; color: #dfe6e9; }
            QPushButton { border: 1px solid #3a3a5e; border-radius: 6px; background: transparent; color: #dfe6e9; padding: 4px; }
            QPushButton:hover { background: #2a2a4e; }
            QLabel#catPhoto { border-radius: 15px; }
        """)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.topcard_layout = QtWidgets.QHBoxLayout()
        self.cat_label = QtWidgets.QLabel('')
        self.topcard_layout.addWidget(self.cat_label) 
        self.cat_photo = QtWidgets.QLabel('')
        self.cat_photo_pixmap = QtGui.QPixmap(catimg)
        self.cat_photo.setPixmap(self.cat_photo_pixmap)
        self.cat_photo.setObjectName("catPhoto")
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
        

    def update_status(self,catfoodstatus, catlastfeedtime, catfeedingtimes):

        foodstatus_api = catfoodstatus
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


        lastfeedtime_api = catlastfeedtime
        lastfeedtime = lastfeedtime_api.state
        if(lastfeedtime == None):
            lastfeedtime = lastfeedtime_api.error
        else:  
            lastfeedtime = format_time_ago(lastfeedtime)                       
        self.lastfeedtime_state.setText(str(lastfeedtime))


        todayfeedingtime_api = catfeedingtimes
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
        self.offset = None

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

        with open(os.path.join(os.path.dirname(sys.executable), "config.json"), "r", encoding= "utf-8") as f:
            config = json.load(f)
        
        self.icon = QtGui.QIcon(os.path.join(os.path.dirname(sys.executable), config["icon"]))
        self.trayicon = QtWidgets.QSystemTrayIcon(self.icon, self)
        self.trayicon.show()

        self.menu = QtWidgets.QMenu()
        self.menu_qaction = self.menu.addAction('Quit')
        self.menu_qaction.triggered.connect(QtWidgets.QApplication.quit)
        self.menu_startonloginaction = self.menu.addAction('Add to startup')
        self.menu_startonloginaction.setCheckable(True)
        self.menu_startonloginaction.triggered.connect(self.toggle_startup)
        self.trayicon.setContextMenu(self.menu)

        self.cat_cards=[]
        for cat in config["cats"]:
            card = CatCard(cat["name"],os.path.join(os.path.dirname(sys.executable), cat["img"]))
            self.cat_cards.append(card)
            self.catcards_layout.addWidget(card)

        self.main_layout.addLayout(self.catcards_layout)



        self.button = QtWidgets.QPushButton("Feed all cats")
        self.main_layout.addWidget(self.button)
        
        self.button.clicked.connect(self.feedcats)

        self.start_refresh()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.start_refresh)
        self.timer.start(60000)
        
    def start_refresh(self):
        self.worker = Worker()
        self.worker.data_ready.connect(self.on_data_ready)
        self.worker.start()

    def on_data_ready(self,data): 
        litterboxbinstatus_api = data["litterboxbin"]
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


        litterboxcleaningstatus_api = data["litterboxcleaning"]
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


        
        apistatus = data["apistatus"]
        apistatusindicator = '#E24B4A'

        self.apistatus_statuscard_label.setText(f'API Status\n{apistatus}\n{datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")}')
        if(apistatus == 'API running.'):
            apistatusindicator = '#00b894'
        self.apistatus_indicator.setStyleSheet(f'font-size: 50px; color: {apistatusindicator}')

        for card in self.cat_cards:
            card.update_status(data[f"{card.cat_name}foodstatus"],data[f"{card.cat_name}lastfeedtime"],data[f"{card.cat_name}feedingtimes"] ) 



    @QtCore.Slot()
    def feedcats(self):        
        for card in self.cat_cards:
            card.feedcat(card.cat_name)


    def mousePressEvent(self, event):
        self.offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if(self.offset is not None):
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None
        
    def toggle_startup(self,checked):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Run',access= winreg.KEY_SET_VALUE) as k:
            if(checked):           
                winreg.SetValueEx(k,'CatWidget',0,winreg.REG_SZ,sys.executable)
            else:
                winreg.DeleteValue(k,'CatWidget')





if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)   
    widget.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnBottomHint  | QtCore.Qt.WindowType.Tool )
    widget.show()

    sys.exit(app.exec())




