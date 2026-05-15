from rest_framework import viewsets, mixins, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Count
from . import (
    models,
    serializers,
    filters as custom_filters,
    permissions as custom_permissions,
)


class FlightViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = custom_filters.FlightFilter
    search_fields = ["route__source__city__name", "route__destination__city__name"]
    ordering_fields = ["departure_time", "arrival_time"]

    def get_queryset(self):
        queryset = (
            models.Flight.objects.all()
            .prefetch_related("crew", "tickets")
            .select_related("route__destination", "route__source", "airplane")
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
                )
            )
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.FlightListSerializer
        if self.action == "retrieve":
            return serializers.FlightDetailSerializer
        return serializers.FlightSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            models.Order.objects.filter(user=self.request.user)
            .prefetch_related("tickets")
            .select_related("user")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.OrderListSerializer
        return serializers.OrderSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = models.AirplaneType.objects.all()
    serializer_class = serializers.AirplaneTypeSerializer
    permission_classes = [custom_permissions.IsAdminOrReadOnly]


class AirplaneViewSet(viewsets.ModelViewSet):
    permission_classes = [custom_permissions.IsAdminOrReadOnly]

    def get_queryset(self):
        return models.Airplane.objects.all().select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AirplaneListSerializer
        if self.action == "upload-image":
            return serializers.AirplaneImageSerializer
        return serializers.AirplaneSerializer

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = serializers.AirplaneImageSerializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    permission_classes = [custom_permissions.IsAdminOrReadOnly]


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.CitySerializer
    permission_classes = [custom_permissions.IsAdminOrReadOnly]

    def get_queryset(self):
        return models.City.objects.all().select_related("country")


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AirportSerializer
    permission_classes = [custom_permissions.IsAdminOrReadOnly]

    def get_queryset(self):
        return models.Airport.objects.all().select_related("city")


class RouteViewSet(viewsets.ModelViewSet):
    permission_classes = [custom_permissions.IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.RouteListSerializer
        if self.action == "retrieve":
            return serializers.RouteDetailSerializer
        return serializers.RouteSerializer

    def get_queryset(self):
        return models.Route.objects.all().select_related("source", "destination")


class CrewViewSet(viewsets.ModelViewSet):
    queryset = models.Crew.objects.all()
    serializer_class = serializers.CrewSerializer
    permission_classes = [permissions.IsAdminUser]
