from django.urls import path
from . import views

urlpatterns = [
    path('', views.AmenitiesListView.as_view(), name='reservation'),
    path('<slug:amenity_slug>/<str:amenity_date>/', views.AmenityDetailView.as_view(), name='amenity_detail')
]
