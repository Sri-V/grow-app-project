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
    path('growhouse_settings/', views.growhouse_settings, name="growhouse_settings"),
    path('crop/new/', views.create_crop, name="create_crop"),
    path('crop/add_variety', views.add_variety, name="add_variety"),
    path('crop/<int:crop_id>/', views.crop_detail, name="crop_detail"),
    path('crop/<int:crop_id>/record/', views.record_crop_info, name="record_crop_info"),
    path('slot/set_qty', views.set_total_slot_quantity, name="set_total_slot_quantity"),
    path('slot/<int:slot_id>/', views.slot_detail, name="slot_detail"),
    path('slot/<int:slot_id>/action', views.slot_action, name="slot_action"),
    path('slot/<int:slot_id>/action/trash', views.trash_crop, name="trash_crop"),
    path('slot/<int:slot_id>/action/harvest', views.harvest_crop, name="harvest_crop"),
    path('slot/<int:slot_id>/action/water', views.water_crop, name="water_crop"),
    path('slot/<int:slot_id>/action/move_tray', views.move_tray, name="move_tray"),
    path('slot/<int:slot_id>/action/note', views.record_note, name="record_note"),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', TemplateView.as_view(template_name="registration/logout.html")),
]
