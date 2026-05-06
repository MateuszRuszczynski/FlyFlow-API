from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from . import models


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(AirplaneSerializer):
    total_places = serializers.IntegerField(read_only=True)
    airplane_type = serializers.CharField(source="airplane_type.name", read_only=True)

    class Meta(AirplaneSerializer.Meta):
        fields = AirplaneSerializer.Meta.fields + ("total_places",)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Country.objects.all(), source="country", write_only=True
    )

    class Meta:
        model = models.City
        fields = ("id", "name", "country", "country_id")


class AirportSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=models.City.objects.all(), source="city", write_only=True
    )

    class Meta:
        model = models.Airport
        fields = ("id", "name", "closest_big_city", "city", "city_id")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta(RouteSerializer.Meta):
        pass


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Crew
        fields = ("id", "first_name", "last_name")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        instance = models.Ticket(**attrs)
        try:
            instance.full_clean(validate_unique=False)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class TicketListSerializer(TicketSerializer):
    flight = serializers.SlugRelatedField(slug_field="route", read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")

    def validate(self, attrs):
        if self.isinstance:
            instance = self.Meta.model(**self.instance.__dict__)
            for attr, value in attrs.item():
                setattr(instance, attr, value)
        else:
            instance = models.Flight(**attrs)
            try:
                instance.full_clean(validate_unique=False)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        return attrs


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.IntegerField(
        source="airplane.total_places", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Flight
        fields = (
            "id",
            "route",
            "airplane_name",
            "airplane_capacity",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewSerializer(read_only=True, many=True)
    taken_places = TicketSerializer(source="tickets", many=True, read_only=True)

    class Meta:
        model = models.Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "taken_places",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = models.Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        with transaction.atomic():
            user = self.context["request"].user
            order = models.Order.objects.create(user=user, **validated_data)
            for ticket_data in tickets_data:
                models.Ticket.objects.create(order=order, **ticket_data)
        return order
