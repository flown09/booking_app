from django.contrib import admin
from .models import Hotel, Room, Booking, RoomImage

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomImageInline]

admin.site.register(Hotel)
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking)