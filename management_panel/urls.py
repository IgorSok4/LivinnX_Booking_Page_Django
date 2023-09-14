from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
<<<<<<< HEAD
    path('tenants/', views.TenantsListView.as_view(), name='admin_tenants'),
    path('admin/tenants/toggle_user_active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
]
=======
    path(r'tenants/^$', views.TenantsListView.as_view(), name='admin_tenants'),
]
>>>>>>> b8b7a38f9007bd786575cef10ef0da2b796630b1
