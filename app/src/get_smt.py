import asyncio
import datetime
from datetime import date
import json
import paho.mqtt.publish as publish
import pytz
from paho.mqtt.client import Client
from app.database.models.cabinets import Ss_main_cabinet
from app.database.models.modules import ss_main_cell, ss_main_marked, ss_main_big_battary_list, \
    ss_main_cabinet_settings_for_auto_marking, ss_main_settings_for_settings, ss_main_cabinet_history
from app.database.models.report import Ss_main_report


pzdc = ss_main_cabinet_history.get(ss_main_cabinet_history.date == date.fromisoformat('2025-01-09'))
print(pzdc.first_data)

