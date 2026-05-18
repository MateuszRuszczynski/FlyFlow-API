from django.contrib import admin
from . import models


class TicketInline(admin.TabularInline):
    model = models.Ticket
    extra = 1


@admin.register(models.Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "airplane_type", "rows", "seats_in_row", "total_places")
    list_filter = ("airplane_type",)
    search_fields = ("name",)


@admin.register(models.Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("__str__", "source", "destination", "distance")
    list_filter = ("source__city", "destination__city")
    search_fields = ("source__name", "destination__name")


@admin.register(models.Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "departure_time",
        "arrival_time",
        "airplane",
        "get_crew_count",
    )
    list_filter = ("departure_time", "route__source", "airplane")
    search_fields = ("route__source__name", "route__destination__name")
    inlines = [TicketInline]

    def get_crew_count(self, obj):
        return obj.crew.count()

    get_crew_count.short_description = "Crew Members"


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "get_ticket_count")
    list_filter = ("created_at", "user")
    inlines = [TicketInline]

    def get_ticket_count(self, obj):
        return obj.tickets.count()

    get_ticket_count.short_description = "Tickets Bought"


@admin.register(models.Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "closest_big_city")
    list_filter = ("city__country",)
    search_fields = ("name", "city__name")


admin.site.register(models.AirplaneType)
admin.site.register(models.Country)
admin.site.register(models.City)
admin.site.register(models.Crew)
admin.site.register(models.Ticket)
