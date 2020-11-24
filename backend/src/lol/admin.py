from django.contrib import admin
from .models import Match, Version, Champion, Queue, Item

# matches
admin.site.register(Match)

# ddragon
admin.site.register(Version)
admin.site.register(Champion)
admin.site.register(Queue)
admin.site.register(Item)
