from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tenants/', views.TenantsListView.as_view(), name='admin_tenants'),
    path('admin/tenants/toggle_user_active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('profile/<str:name>-<str:surname>/<int:user_id>', views.admin_tenant_profile, name='admin_tenant_profile'),
    path('reservation_delete/<int:reservation_id>/', views.reservation_delete, name='admin_reservation_delete'),
    path('admin/tenants/toggle_reservation_active/<int:reservation_id>/', views.toggle_reservation_active, name='toggle_reservation_active'),
    path('delete_comment/<int:user_id>/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]