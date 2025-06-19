from django.contrib import admin
from .models import Hotel, Room, Booking, RoomImage, CustomUser, HotelImage
from django.contrib.auth.admin import UserAdmin

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1


admin.site.register(RoomImage)
admin.site.register(HotelImage)
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating')
    search_fields = ('name', 'city', 'rating')
    inlines = [HotelImageInline]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'capacity', 'is_available')
    list_filter = ('hotel', 'is_available')
    search_fields = ('name',)
    inlines = [RoomImageInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'status')
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = ('user__username', 'room__name')
    actions = ['confirm_booking', 'cancel_booking']

    @admin.action(description='Подтвердить выбранные бронирования')
    def confirm_booking(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} бронирований подтверждено.")

    @admin.action(description='Отменить выбранные бронирования')
    def cancel_booking(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} бронирований отменено.")

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_superuser', 'is_staff', 'first_name', 'last_name', 'phone_number')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone_number',)}),
    )
