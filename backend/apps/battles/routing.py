"""
Routes WebSocket (Django Channels) de l'app 'battles'.
Les consumers (DuelConsumer, TournamentConsumer, ...) seront implementes
en phase 2, en meme temps que les modeles Match / BattleRoom.
"""
from django.urls import re_path

websocket_urlpatterns = [
    # re_path(r"ws/battles/duel/(?P<room_code>\w+)/$", consumers.DuelConsumer.as_asgi()),
]
