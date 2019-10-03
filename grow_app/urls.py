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
    path('inventory/add_barcodes', views.add_barcodes, name="add_barcodes"),
    path('golden_trays/', views.golden_trays_home, name="golden_trays_home"),
    path('golden_trays/search_crop', views.search_crop, name="search_crop"),
    path('growhouse_settings/', views.growhouse_settings, name="growhouse_settings"),
    path('crop/new/', views.create_crop, name="create_crop"),
    path('crop/new/autofill', views.variety_autofill, name="variety_autofill"),
    path('crop/add_variety', views.add_variety, name="add_variety"),
    path('crop/<int:crop_id>/record_notes', views.record_notes, name="record_notes"),
    path('crop/<int:crop_id>/record', views.record_crop_info, name="record_crop_info"),
    path('crop/<int:crop_id>/', views.crop_detail, name="crop_detail"),
    path('crop/<int:crop_id>/edit/', views.edit_crop, name="edit_crop"),
    path('crop/add_attributes/', views.add_crop_attributes, name="add_crop_attributes"),
    path('crop/add_attribute', views.add_crop_attribute, name="add_crop_attribute"),
    path('crop/add_option', views.add_attribute_option, name="add_attribute_option"),
    path('slot/set_qty', views.set_total_slot_quantity, name="set_total_slot_quantity"),
    path('slot/<int:slot_id>/', views.slot_detail, name="slot_detail"),
    path('slot/<int:slot_id>/action', views.slot_action, name="slot_action"),
    path('slot/<int:slot_id>/action/trash', views.trash_crop, name="trash_crop"),
    path('slot/<int:slot_id>/action/harvest', views.harvest_crop, name="harvest_crop"),
    path('slot/<int:slot_id>/action/water', views.water_crop, name="water_crop"),
    path('barcode/<str:barcode_text>/', views.parse_barcode, name="parse_barcode"),
    path('sanitation_records/', views.sanitation_records, name='sanitation_records'),
    path('record/<int:record_id>/edit', views.update_crop_record, name="update_crop_record"),
    path('record/<int:record_id>/delete', views.delete_record, name="delete_record"),
    path('environment_data', views.environment_data, name="environment_data"),
    path('inventory/add_product', views.add_product, name="add_product"),
    path('inventory/catalog', views.catalog, name="catalog")
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', TemplateView.as_view(template_name="registration/logout.html")),
]
