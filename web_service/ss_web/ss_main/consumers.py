import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        action = text_data_json['action']

        if action == 'load_cabinets':
            response = await self.load_cabinets()
        elif action == 'load_cells':
            cabinet_id = text_data_json['cabinet_id']
            response = await self.load_cells(cabinet_id)
        elif action == 'load_cell':
            vir_sn_eid = text_data_json['vir_sn_eid']
            response = await self.load_cell(vir_sn_eid)
        else:
            # Если action не соответствует ни одному из ожидаемых значений
            response = {"error": "Unknown action"}

        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def load_cabinets(self):
        from .models import Cabinet
        cabinets = Cabinet.objects.all()
        cabinets_data = [
            {"city": cabinet.city, "shkaf_id": cabinet.shkaf_id, "zone": cabinet.zone,
             "location": cabinet.location, "street": cabinet.street, "extra_inf": cabinet.extra_inf}
            for cabinet in cabinets
        ]
        return {"type": 'cabinets', 'data': cabinets_data}

    @database_sync_to_async
    def load_cells(self, cabinet_id):
        from .models import Cell
        cells = Cell.objects.filter(cabinet_id=cabinet_id).all()
        cells_data = [
            {"id": cell.endpointid, "station_id": cell.cabinet_id.shkaf_id, "status": cell.status,
             "charge": cell.cap_percent}
            for cell in cells
        ]

        return {"type": 'cells', 'data': cells_data}

    @database_sync_to_async
    def load_cell(self, vir_sn_eid):
        from .models import Cell
        cell = Cell.objects.get(vir_sn_eid=vir_sn_eid)
        cell_data = {
            "name": cell.endpointid,
            "vid": cell.vid,
            "sn": cell.sn,
            "sw_ver": cell.sw_ver
        }
        return {"type": 'cell', 'data': cell_data}


class MyReports(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self):
        await self.send(text_data=json.dumps("Репорты"))
