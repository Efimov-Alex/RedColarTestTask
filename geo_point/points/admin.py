from django.contrib import admin
from django.utils.html import format_html
from .models import LocationPoint, PointMessage

@admin.register(LocationPoint)
class LocationPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'address', 'created_at', 'get_coordinates_link')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Координаты', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_coordinates_link(self, obj):
        url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
        return format_html(f'<a href="{url}" target="_blank">🗺️ На карте</a>')
    get_coordinates_link.short_description = 'Карта'

@admin.register(PointMessage)
class PointMessageAdmin(admin.ModelAdmin):
    list_display = ('truncated_text', 'point', 'user', 'created_at')
    list_filter = ('created_at', 'point')
    search_fields = ('text', 'point__name', 'user__username')
    readonly_fields = ('created_at',)
    
    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = 'Текст'