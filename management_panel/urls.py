from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tenants/', views.TenantsListView.as_view(), name='admin_tenants'),
    path('admin/tenants/toggle_user_active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
]