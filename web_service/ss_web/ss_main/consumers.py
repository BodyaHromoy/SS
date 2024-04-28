from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        if action == 'load_cabinets':
            response = await self.load_cabinets()
        elif action == 'load_cells':
            cabinet_id = text_data_json['cabinet_id']
            response = await self.load_cells(cabinet_id)
        elif action == 'load_cell':
            cell_id = text_data_json['cell_id']
            response = await self.load_cell(cell_id)

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
        cells = Cell.objects.filter(cabinet_id=cabinet_id)
        cells_data = [
            {"id": cell.id, "name": cell.name, "capacity": cell.capacity}
            for cell in cells
        ]
        return {'data': cells_data}

    @database_sync_to_async
    def load_cell(self, cell_id):
        from .models import Cell
        cell = Cell.objects.get(id=cell_id)
        cell_data = {
            "id": cell.id,
            "name": cell.name,
            "capacity": cell.capacity
        }
        return {'data': cell_data}
