from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path(r'tenants/^$', views.TenantsListView.as_view(), name='admin_tenants'),
]
