import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from cinema.models import ShowTime, ReservationSeat


class SeatConsumer(AsyncWebsocketConsumer):
    def get_showtime(self, showtime_id):
        return ShowTime.objects.get(id=showtime_id)

    def get_reservation_seats_ids(self, showtime):
        return list(
            ReservationSeat.objects.filter(
                show_time=showtime,
                reservation__status__in=['pending', 'confirmed']
            ).values_list("seat_id", flat=True)
        )

    async def connect(self):
        self.showtime_id = self.scope['url_route']['kwargs']['showtime_id']
        self.group_name = f"showtime_{self.showtime_id}"
        self.showtime = await database_sync_to_async(self.get_showtime)(self.showtime_id)

        reserved_seat_ids = await database_sync_to_async(self.get_reservation_seats_ids)(self.showtime)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'seat_update',
                'data': {
                    'action': 'reserved',
                    'seats': reserved_seat_ids,
                }
            }
        )


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def seat_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
