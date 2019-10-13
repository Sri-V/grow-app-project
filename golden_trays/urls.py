from django.urls import path
from golden_trays import views

urlpatterns = [
    path('golden_trays/add_barcodes', views.add_barcodes, name="add_barcodes"),
    path('golden_trays/', views.golden_trays_home, name="golden_trays_home"),
    path('golden_trays/search_crop', views.search_crop, name="search_crop"),
    path('crop/new/', views.create_crop, name="create_crop"),
    path('crop/<int:crop_id>/record_notes', views.record_notes, name="record_notes"),
    path('crop/<int:crop_id>/record', views.record_crop_info, name="record_crop_info"),
    path('crop/<int:crop_id>/', views.crop_detail, name="crop_detail"),
    path('crop/<int:crop_id>/edit/', views.edit_crop, name="edit_crop"),
    path('crop/add_attributes/', views.add_crop_attributes, name="add_crop_attributes"),
    path('crop/add_attribute', views.add_crop_attribute, name="add_crop_attribute"),
    path('crop/add_option', views.add_attribute_option, name="add_attribute_option"),
    path('slot/<int:slot_id>/', views.slot_detail, name="slot_detail"),
    path('slot/<int:slot_id>/action/trash', views.trash_crop, name="trash_crop"),
    path('slot/<int:slot_id>/action/harvest', views.harvest_crop, name="harvest_crop"),
    path('slot/<int:slot_id>/action/water', views.water_crop, name="water_crop"),
    path('barcode/<str:barcode_text>/', views.parse_barcode, name="parse_barcode"),
    path('record/<int:record_id>/edit', views.update_crop_record, name="update_crop_record"),
    path('record/<int:record_id>/delete', views.delete_record, name="delete_record"),
]