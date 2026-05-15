from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "airport"

router = routers.DefaultRouter()
router.register("airplane_types", views.AirplaneTypeViewSet, basename="airplane_type")
router.register("airplanes", views.AirplaneViewSet, basename="airplane")
router.register("orders", views.OrderViewSet, basename="order")
router.register("countries", views.CountryViewSet, basename="country")
router.register("cities", views.CityViewSet, basename="city")
router.register("airports", views.AirportViewSet, basename="airport")
router.register("routes", views.RouteViewSet, basename="route")
router.register("crew", views.CrewViewSet, basename="crew")
router.register("flights", views.FlightViewSet, basename="flight")

urlpatterns = [path("", include(router.urls))]
