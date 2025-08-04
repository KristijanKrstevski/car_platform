"""
URL configuration for dealership_menagment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# dealership_menagment/urls.py (or wherever your main urls.py is)

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from dealership_app import views
from dealership_app import frontend_views
urlpatterns = [

    path('', frontend_views.index, name='frontend_index'),
    path('vehicles/', frontend_views.vehicle_list, name='frontend_vehicles'),
    path('vehicles/<int:pk>/', frontend_views.vehicle_detail, name='frontend_vehicle_detail'),
    path('ajax/models/', frontend_views.ajax_models, name='ajax_models'),
    # ✅ Keep Django's built-in admin
    path('admin/', admin.site.urls),

    # ✅ Use a different prefix for your custom dashboard
    path('dashboard/', views.admin_dashboard, name="admin_dashboard"),

    # ✅ Cars management (custom admin views)
    path('dashboard/cars/', views.admin_car_list, name="admin_car_list"),
    path('dashboard/cars/add/', views.admin_car_add, name="admin_car_add"),
    path('dashboard/cars/<int:pk>/edit/', views.admin_car_edit, name="admin_car_edit"),
    path('dashboard/cars/<int:pk>/delete/', views.admin_car_delete, name="admin_car_delete"),
    path('ajax/delete-car-image/<int:pk>/', views.ajax_delete_car_image, name="ajax_delete_car_image"),
    path('ajax/load-models/', views.ajax_load_models, name='ajax_load_models'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
