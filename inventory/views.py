from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from inventory.models import Crop, CropRecord, Slot, Variety, InHouse, WeekdayRequirement, InventoryAction
from inventory.forms import *
from datetime import datetime
from dateutil import parser
from dateutil import tz

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


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
    add_variety_form = AddVarietyForm()
    return render(request, "inventory/growhouse_settings.html", context={"total_slot_count": total_slot_count, "form": add_variety_form})

@login_required
def set_total_slot_quantity(request):
    """POST: Update the number of total Slot objects, redirect to homepage."""
    phase = str(request.POST["phase"])
    racks = int(request.POST["racks"])
    rows = int(request.POST["rows"])
    slots = int(request.POST["slots"])
    #current_slot_count = Slot.objects.count()
    if Slot.objects.count() > 0:
        try:
            last_slot = Slot.objects.filter(barcode__startswith=phase).order_by("-barcode")[0]
            next_index = int(str(last_slot.barcode)[1:4]) + 1
        except IndexError:
            next_index = 1
    else:
        next_index = 1

    for ra in range(next_index, next_index + racks):
        print("Adding rack ", ra)
        for ro in range(1, rows):
            for sl in range(1,slots):
                barcode = phase + str(ra).zfill(3) + str(ro).zfill(2) + str(sl).zfill(2)
                Slot.objects.create(barcode=barcode)

    return redirect(growhouse_settings)


@login_required
def add_variety(request):
    """POST: Adds Variety Objects"""
    form = AddVarietyForm(request.POST)
    if form.is_valid():
        variety_name = form.cleaned_data["name"]
        days_germ = form.cleaned_data["days_germ"]
        days_grow = form.cleaned_data["days_grow"]
        Variety.objects.create(name=variety_name, days_germ=days_germ, days_grow=days_grow)

        return redirect(growhouse_settings)

    total_slot_count = Slot.objects.count()
    return render(request, "inventory/growhouse_settings.html", context={"total_slot_count": total_slot_count, "form": form})


@login_required
def create_crop(request):
    """GET: Display a form for new crop data.
    POST: Accept form submission for new crop data, redirect to the new crop's detail page."""
    if request.method == 'GET':
        variety_list = Variety.objects.all()

        slot_list = Slot.objects.filter(current_crop=None)
        current_datetime = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        variety = variety_list[0]

        return render(request, "inventory/new_crop.html",
                      context={"variety_list": variety_list, "slot_list": slot_list, "days_germ": variety.days_germ, "days_grow": variety.days_grow})

    if request.method == 'POST':
        variety_name = request.POST["variety"]
        tray_size = str(request.POST["tray-size"])
        delivered_live = (request.POST["delivered-live"] == 'True')
        germination_length = int(request.POST["germination-length"])
        grow_length = int(request.POST["grow-length"])
        slot_barcode = request.POST["slot-barcode"]
        variety = Variety.objects.get(name=variety_name)
        
        slot = get_object_or_404(Slot, barcode=slot_barcode)
        if slot.current_crop is not None:
            return HttpResponseBadRequest(f'Slot {slot.id} already contains a crop!')
        
        new_crop = Crop.objects.create(variety=variety, tray_size=tray_size, live_delivery=delivered_live,
                                       exp_num_germ_days=germination_length, exp_num_grow_days=grow_length)
        slot.current_crop = new_crop
        slot.save()
        
        # Create crop record for this event
        CropRecord.objects.create(crop=new_crop, record_type='SEED')
        # Redirect the user to the slot details page
        return redirect(slot_detail, slot_id=slot.id)


@login_required
def crop_detail(request, crop_id):
    """GET: Display the crop's details and history. The details include the type of crop, tray size,
    delivered live, ect. Page also provides a link to the crop's slot."""
    crop = Crop.objects.get(id=crop_id)

    edit = request.GET.get('edit', False)

    record_id = int(request.GET.get('id', -1))

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

    record_types = [record[1] for record in CropRecord.RECORD_TYPES]  # This returns a list of all the readable crop record types

    return render(request, "inventory/crop_details.html", context={"history": all_records, "crop": crop, "records": records, "notes": notes, "seed": seed, "grow": grow, "water": water,
                           "harvest": harvest, "delivered": delivered, "trash": trash, "returned": returned, "record_types": record_types, "edit": edit, "record_id": record_id })


@login_required
def record_crop_info(request, crop_id):
    """POST: Record a timestampped CropRecord event into the history of this crop's life."""
    current_crop = Crop.objects.get(id=crop_id)
    record_type = request.POST["record-type"]
    record_date = request.POST["date"]
    datetime_object = parser.parse(record_date).replace(tzinfo=tz.tzlocal())
    record_note = request.POST["note"]
    new_crop_record = CropRecord.objects.create(crop=current_crop, record_type=record_type, note=record_note)
    new_crop_record.date = datetime_object
    new_crop_record.save()
    return redirect(crop_detail, crop_id=current_crop.id)

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
    return render(request, "inventory/slot_details.html", context={"slot_id": slot_id, "current_crop": current_crop, "open_slots": open_slots })


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
    return redirect(slot_detail, slot_id=slot_id)


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
    slot_barcode = request.POST["slot-destination-barcode"]
    new_lifecycle = str(request.POST["new-lifecycle-moment"])

    arriving_slot = get_object_or_404(Slot, barcode=slot_barcode)
    if arriving_slot.current_crop is not None:
        return HttpResponseBadRequest(f'Slot {arriving_slot.id} already contains a crop!')
    
    arriving_slot.current_crop = leaving_slot.current_crop
    leaving_slot.current_crop = None
    if new_lifecycle is not '-- none --':
        date = datetime.now()
        CropRecord.objects.create(record_type=new_lifecycle, date=date, note="Tray Moved",
                                  crop=arriving_slot.current_crop)
    leaving_slot.save()
    arriving_slot.save()
    return redirect(slot_detail, slot_id=arriving_slot.id)


@login_required
def record_note(request, slot_id):
    """POST: Record that the crop has been moved and redirect user to homepage."""
    crop = Slot.objects.get(id=slot_id).current_crop
    note = request.POST["note"]
    date = datetime.now()
    CropRecord.objects.create(record_type="NOTE", date=date, note=note, crop=crop)
    return redirect(slot_detail, slot_id=slot_id)


@login_required
def delete_record(request, record_id):
    """GET: Deletes the crop record with the specified record id"""
    crop_record = CropRecord.objects.get(id=record_id)
    crop_record.delete()
    crop = crop_record.crop
    return redirect(crop_detail, crop_id=crop.id)

@login_required
def update_crop_record(request, record_id):
    """POST: Updates the specified record"""
    crop_record = CropRecord.objects.get(id=record_id)
    updated_date = request.POST["date"]
    datetime_object = parser.parse(updated_date).replace(tzinfo=tz.tzlocal())
    updated_note = request.POST["note"]
    crop_record.date = datetime_object
    crop_record.note = updated_note
    crop_record.save()
    crop = crop_record.crop
    return redirect(crop_detail, crop_id=crop.id)

@login_required
def parse_barcode(request, barcode_text):
    slot = get_object_or_404(Slot, barcode=barcode_text)
    return redirect(slot_detail, slot_id=slot.id)

@login_required
def sanitation_records(request):
    """GET: Displays the page with the current sanitation records
    POST: Records the new sanitation record"""
    if request.method == 'GET':
        sanitation_record_list = SanitationRecord.objects.all().order_by('-date')
        form = SanitationRecordForm(initial={'date': datetime.now().strftime("%m/%d/%Y %H:%M") })
        return render(request, "inventory/sanitation_records.html",
                      context={"record_list": sanitation_record_list, "form": form })

    if request.method == 'POST':
        form = SanitationRecordForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            employee_name = form.cleaned_data['employee_name']
            equipment_sanitized = form.cleaned_data['equipment_sanitized']
            chemicals_used = form.cleaned_data['chemicals_used']
            note = form.cleaned_data['note']

            SanitationRecord.objects.create(date=date, employee_name=employee_name, equipment_sanitized=equipment_sanitized, chemicals_used=chemicals_used, note=note)

            return redirect(sanitation_records)


@login_required
def variety_autofill(request):
    variety = request.GET.get('variety', None)
    data = {
        'days_germ': Variety.objects.get(name=variety).days_germ,
        'days_grow': Variety.objects.get(name=variety).days_grow
    }
    return JsonResponse(data)

@login_required
def inventory_home(request):
    return render(request, "inventory/inventory_home.html")

@login_required
def inventory_overview(request):
    varieties = Variety.objects.all()
    for v in varieties:
        # InHouse.objects.create(variety=v, num_small=0, num_medium=0, num_big=0)
        try:
            InHouse.objects.create(variety=v, num_small=0, num_medium=0, num_big=0)
        except:
            pass

    in_house = InHouse.objects.all()
    return render(request, 'inventory/inventory_overview.html', context={'in_house':in_house})

@login_required
def inventory_seed(request):
    today = datetime.today().weekday()
    if request.method == 'GET':
        for v in Variety.objects.all():
            if len(WeekdayRequirement.objects.filter(plant_day=today).filter(variety=v)) == 0:
                WeekdayRequirement.objects.create(variety=v, plant_day=today, num_small=0, num_medium=0, num_big=0)

        to_do = WeekdayRequirement.objects.filter(plant_day=today).order_by('num_big')
        return render(request, 'inventory/inventory_seed.html', context={'to_do':to_do})
    
    if request.method == 'POST':
        for v in Variety.objects.all():
            try:
                big = int(request.POST['form-seed-big-' + v.name])
                medium = int(request.POST['form-seed-medium-' + v.name])
                small = int(request.POST['form-seed-small-' + v.name])
                in_house = InHouse.objects.get(variety=v)
                in_house.num_big += big
                in_house.num_medium += medium
                in_house.num_small += small
                in_house.save()

                note = "big: {}, medium: {}, small: {}".format(big, medium, small)
                var_obj = Variety.objects.get(name=v)
                InventoryAction.objects.create(variety=var_obj, action_type='SEED', note=note)
            except KeyError:
                pass # In case there's a variety inconsistency
        
        # Redirect the user to the slot details page
        return redirect(inventory_overview)

@login_required
def inventory_kill(request):
    today = datetime.today().weekday()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_kill.html', context={'variety_list':Variety.objects.all()})
    
    if request.method == 'POST':
        try:
            variety = request.POST['form-kill-variety']
            big = int(request.POST['form-kill-big'])
            medium = int(request.POST['form-kill-medium'])
            small = int(request.POST['form-kill-small'])
            note = request.POST['form-kill-reason']
            var_obj = Variety.objects.get(name=variety)
            in_house = InHouse.objects.get(variety=var_obj)
            in_house.num_big = in_house.num_big - big if big <= in_house.num_big else 0
            in_house.num_medium = in_house.num_medium - medium if medium <= in_house.num_medium else 0
            in_house.num_small = in_house.num_small - small if small <= in_house.num_small else 0
            in_house.save()
            InventoryAction.objects.create(variety=var_obj, action_type='KILL', note=note)
        except KeyError as e:
            print (e)
            pass # In case there's a variety inconsistency
        
        # Redirect the user to the slot details page
        return redirect(inventory_overview)
