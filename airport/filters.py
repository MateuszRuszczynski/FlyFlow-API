import django_filters
from . import models


class FlightFilter(django_filters.FilterSet):
    departure_date_from = django_filters.DateTimeFilter(
        field_name="departure_time", lookup_expr="gte"
    )
    departure_date_to = django_filters.DateTimeFilter(
        field_name="departure_time", lookup_expr="lte"
    )

    source_airport = django_filters.CharFilter(
        field_name="route__source__name", lookup_expr="icontains"
    )
    destination_airport = django_filters.CharFilter(
        field_name="route__destination__name", lookup_expr="icontains"
    )

    class Meta:
        model = models.Flight
        fields = [
            "route__source__city__name",
            "route__destination__city__name",
        ]
