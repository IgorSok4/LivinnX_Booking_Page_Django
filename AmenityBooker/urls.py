from django.urls import path
from . import views

urlpatterns = [
    path('', views.AmenitiesListView.as_view(), name='reservation'),
    path('<slug:amenity_slug>/<str:amenity_date>/', views.AmenityDetailView.as_view(), name='amenity_detail'),
    path('make_reservation/', views.make_reservation, name='make_reservation'),
    # path('api/reserve/<slug:amenity_slug>/<str:amenity_date_str>/', views.api_reserve_hours, name='api_reserve_hours'),
]
