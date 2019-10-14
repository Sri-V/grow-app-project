"""grow_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from inventory import views
import golden_trays.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name="home"),
    path('inventory/', views.inventory_home, name='inventory_home'),
    path('inventory/overview/', views.inventory_overview, name='inventory_overview'),
    path('inventory/seed/', views.inventory_seed, name='inventory_seed'),
    path('inventory/harvest/bulk/', views.inventory_harvest_bulk, name='inventory_harvest_bulk'),
    path('inventory/harvest/variety/', views.inventory_harvest_variety, name='inventory_harvest_variety'),
    path('inventory/harvest/single/', views.inventory_harvest_single, name='inventory_harvest_single'),
    path('inventory/kill/', views.inventory_kill, name='inventory_kill'),
    path('inventory/plan/', views.inventory_plan, name='inventory_plan'),
    path('inventory/plan/autofill', views.weekday_autofill, name="weekday_autofill"),
    path('growhouse_settings/', views.growhouse_settings, name="growhouse_settings"),
    path('crop/new/autofill', views.variety_autofill, name="variety_autofill"),
    path('crop/add_variety', views.add_variety, name="add_variety"),
    path('slot/set_qty', views.set_total_slot_quantity, name="set_total_slot_quantity"),
    path('sanitation_records/', views.sanitation_records, name='sanitation_records'),
    path('environment_data', views.environment_data, name="environment_data"),
    path('inventory/add_product', views.add_product, name="add_product"),
    path('inventory/catalog', views.catalog, name="catalog")
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', TemplateView.as_view(template_name="registration/logout.html")),
    path('', include(golden_trays.urls))
]
