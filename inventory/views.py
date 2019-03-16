from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from inventory.models import Crop, CropRecord, Slot, Variety
from datetime import datetime

from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def homepage(request):
    """GET: Display a homepage that offers links to detail pages for crops and slots."""
    total_slot_count = Slot.objects.count()
    return render(request, "inventory/index.html", context={"total_slot_count": total_slot_count})

@login_required
def growhouse_settings(request):
    """GET: Shows the setup page which contains forms for the inital setup of the grow space including
    allowing a user to set the original number of slots and adding varieties"""
    total_slot_count = Slot.objects.count()
    return render(request, "inventory/greenhouse_settings.html", context={"total_slot_count": total_slot_count})

@login_required
def set_total_slot_quantity(request):
    """POST: Update the number of total Slot objects, redirect to homepage."""
    desired_slot_count = int(request.POST["quantity"])
    current_slot_count = Slot.objects.count()
    
    if desired_slot_count >= current_slot_count:
        for slot in range(desired_slot_count - Slot.objects.count()):
            Slot.objects.create()
    else:
        # Reducing the number of trays is currently not a supported operation.
        return HttpResponseBadRequest()
            
    return redirect(growhouse_settings)


@login_required
def add_variety(request):
    """POST: Adds Variety Objects"""
    variety_name = request.POST["variety-name"]
    days_to_harvest = request.POST["days-to-harvest"]
    Variety.objects.create(name=variety_name, days_plant_to_harvest=days_to_harvest)
    return redirect(growhouse_settings)


@login_required
def create_crop(request):
    """GET: Display a form for new crop data.
    POST: Accept form submission for new crop data, redirect to the new crop's detail page."""
    if request.method == 'GET':
        variety_list = Variety.objects.all()
        slot_list = Slot.objects.filter(current_crop=None)
        return render(request, "inventory/new_crop.html", context={"variety_list": variety_list, "slot_list": slot_list})

    if request.method == 'POST':
        # TODO -- add input verification check
        variety_name = request.POST["variety"]
        tray_size = str(request.POST["tray-size"])
        delivered_live = (request.POST["delivered-live"] == 'True')
        germination_length = int(request.POST["germination-length"])
        grow_length = int(request.POST["grow-length"])
        designated_slot_id = int(request.POST["designated-slot-id"])
        variety = Variety.objects.get(name=variety_name)
        # Check that the destination slot exists and it is empty
        try:
            designated_slot = Slot.objects.get(id=designated_slot_id)
        except Slot.DoesNotExist:
            return HttpResponseBadRequest()
        if designated_slot.current_crop is not None:
            return HttpResponseBadRequest()
        # Create the crop object
        new_crop = Crop.objects.create(variety=variety, tray_size=tray_size, live_delivery=delivered_live, exp_num_germ_days=germination_length, exp_num_grow_days=grow_length)
        # Update the corresponding slot with that crop
        designated_slot.current_crop = new_crop
        designated_slot.save()
        # Create crop record for this event
        CropRecord.objects.create(crop=new_crop, record_type='SEED')
        # Redirect the user to the slot details page
        return redirect('/slot/' + str(designated_slot_id) + '/')


@login_required
def crop_detail(request, crop_id):
    """GET: Display the crop's details and history. The details include the type of crop, tray size,
    delivered live, ect. Page also provides a link to the crop's slot."""
    crop = Crop.objects.get(id=crop_id)

    all_records = CropRecord.objects.filter(crop=crop_id).order_by("-date")

    # FIXME -- handle this selection client-side via template filtering and selection
    try:
        records = CropRecord.objects.filter(crop=crop_id).exclude(record_type='NOTE').order_by('-date')
    except Exception:
        records = None
    try:
        notes = CropRecord.objects.filter(crop=crop_id).filter(record_type='NOTE').order_by('-date')
    except Exception:
        notes = None
    try:
        seed = CropRecord.objects.filter(crop=crop_id).filter(record_type='SEED').order_by('-date')[0]
    except Exception:
        seed = None
    try:
        grow = CropRecord.objects.filter(crop=crop_id).filter(record_type='GROW').order_by('-date')[0]
    except Exception:
        grow = None
    try:
        water = CropRecord.objects.filter(crop=crop_id).filter(record_type='WATER').order_by('-date')[0]
    except Exception:
        water = None
    try:
        harvest = CropRecord.objects.filter(crop=crop_id).filter(record_type='HARVEST').order_by('-date')[0]
    except Exception:
        harvest = None
    try:
        delivered = CropRecord.objects.filter(crop=crop_id).filter(record_type='DELIVERED').order_by('-date')[0]
    except Exception:
        delivered = None
    try:
        trash = CropRecord.objects.filter(crop=crop_id).filter(record_type='TRASH').order_by('-date')[0]
    except Exception:
        trash = None
    try:
        returned = CropRecord.objects.filter(crop=crop_id).filter(record_type='RETURNED').order_by('-date')[0]
    except Exception:
        returned = None

    return render(request, "inventory/crop_details.html", context={"history": all_records, "crop": crop, "records": records, "notes": notes, "seed": seed, "grow": grow, "water": water,
                           "harvest": harvest, "delivered": delivered, "trash": trash, "returned": returned})


@login_required
def record_crop_info():
    """POST: Record a timestampped event into the history of this crop's life."""
    return None


@login_required
def update_crop_lifecycle():
    """POST: Advance the crop from one lifecycle moment to another."""
    return None


@login_required
def slot_detail(request, slot_id):
    """GET: Displays the details of current crop in the slot and all the buttons used to control a tray in the greenhouse.
    Provides buttons and forms to perform tray actions.This is the page that people using the barcode scanner are going to
     see as they're working all day, so it needs to feel like a control panel."""
    current_crop = Slot.objects.get(id=slot_id).current_crop
    open_slots = Slot.objects.filter(current_crop=None)

    return render(request, "inventory/slot_details.html", context={"slot_id": slot_id, "current_crop": current_crop, "open_slots": open_slots})


@login_required
def slot_action():
    """GET: Display a form for a user to record an action on a tray.
    POST: Update the state of the Tray and make a CropRecord of whatever was done."""
    return None


@login_required
def harvest_crop(request, slot_id):
    """POST: Remove the crop from its tray, record crop history as harvest, and redirect to crop detail page."""
    slot = Slot.objects.get(id=slot_id)
    current_crop = slot.current_crop
    slot.current_crop = None
    slot.save()
    CropRecord.objects.create(crop=current_crop, record_type="HARVEST")
    return redirect(crop_detail, crop_id=current_crop.id)


@login_required
def trash_crop(request, slot_id):
    """POST: Record that the crop has been trashed and redirect user to homepage."""
    slot = Slot.objects.get(id=slot_id)
    crop = slot.current_crop
    slot.current_crop = None
    slot.save()
    reason_for_trash = request.POST["reason-for-trash-text"]
    CropRecord.objects.create(crop=crop, record_type='TRASH', note=reason_for_trash)
    return redirect('/slot/' + str(slot_id) + '/')


@login_required
def water_crop(request, slot_id):
    """POST: Record that the crop has been watered and redirect user to homepage."""
    slot = Slot.objects.get(id=slot_id)
    crop = slot.current_crop
    rec = CropRecord.objects.create(crop=crop, record_type='WATER', date=datetime.now(), note='')
    return redirect(slot_detail, slot_id=slot_id)


@login_required
def move_tray(request, slot_id):
    """POST: Update the database with the tray that has been moved"""
    leaving_slot = Slot.objects.get(id=slot_id)
    arriving_slot_id = int(request.POST["slot-destination-id"])
    arriving_slot = Slot.objects.get(id=arriving_slot_id)
    arriving_slot.current_crop = leaving_slot.current_crop
    leaving_slot.current_crop = None
    leaving_slot.save()
    arriving_slot.save()
    return redirect('/slot/' + str(arriving_slot_id) + '/')


@login_required
def record_note(request, slot_id):
    """POST: Record that the crop has been moved and redirect user to homepage."""
    crop = Slot.objects.get(id=slot_id).current_crop
    note = request.POST["note"]
    date = datetime.now()
    CropRecord.objects.create(record_type="NOTE", date=date, note=note, crop=crop)
    return redirect(slot_detail, slot_id=slot_id)



