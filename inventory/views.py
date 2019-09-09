from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from inventory.models import Crop, CropAttribute, CropAttributeOption, CropRecord, Slot, Variety, WeekdayRequirement, InventoryAction, KillReason, CropGroup
from inventory.forms import *
from datetime import date, datetime, timedelta
from dateutil import parser
from google_sheets.upload_to_sheet import upload_data_to_sheets
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import os
import json

@login_required
def golden_trays_home(request):
    """GET: Display the homepage for the golden trays"""
    return render(request, "inventory/golden_trays_home.html")

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
    free_slot_count = Slot.objects.filter(current_crop__isnull=True).count()
    add_variety_form = AddVarietyForm()
    return render(request, "inventory/growhouse_settings.html", context={"total_slot_count": total_slot_count, "free_slot_count": free_slot_count, "form": add_variety_form})

@login_required
def set_total_slot_quantity(request):
    """POST: Update the number of total Slot objects, redirect to homepage."""
    phase = "G"  # Phase will always be grow since we are on tracking golden trays in grow
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
        for ro in range(1, rows + 1):
            for sl in range(1, slots + 1):
                barcode = phase + str(ra).zfill(3) + str(ro).zfill(2) + str(sl).zfill(2)
                # Create slot object.
                slot = Slot.objects.create()
                # Add slot id to make barcode unique.
                slot.barcode = barcode + str(slot.id).zfill(2)
                slot.save()

    return redirect(growhouse_settings)


@login_required
def add_variety(request):
    """POST: Adds Variety Objects"""
    form = AddVarietyForm(request.POST)
    if form.is_valid():
        variety_name = form.cleaned_data["name"]
        Variety.objects.create(name=variety_name)

        return redirect(growhouse_settings)

    total_slot_count = Slot.objects.count()
    return render(request, "inventory/growhouse_settings.html", context={"total_slot_count": total_slot_count, "form": form})

@login_required
def record_notes(request, crop_id):
    """POST: Adds or updates notes for a given crop"""
    form = CropNotesForm(request.POST)
    crop = Crop.objects.get(id=crop_id)
    if form.is_valid():
        notes = form.cleaned_data["notes"]
        crop.notes = notes
        crop.save()

    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)


@login_required
def create_crop(request):
    """GET: Display a form for new crop data.
    POST: Accept form submission for new crop data, redirect to the new crop's detail page."""
    if request.method == 'GET':
        variety_list = Variety.objects.all()
        new_crop_barcode = request.GET.get('barcode', '')
        auto_fill_barcode = request.GET.get('autofill-barcode', False)
        print("autofill barcode", auto_fill_barcode)
        initial_dict = {'date_seeded': datetime.now().strftime("%m/%d/%Y")}
        if auto_fill_barcode:
            selected_crop = Slot.objects.get(barcode=auto_fill_barcode).current_crop

            initial_dict['variety'] = selected_crop.variety
            initial_dict['days_germinated'] = selected_crop.days_in_germ()
            initial_dict['seeding_density'] = selected_crop.seeding_density
            initial_dict['notes'] = selected_crop.notes

            crop_attribute_options = selected_crop.attributes.all()
            print("crop attributes ", crop_attribute_options)
            for option in crop_attribute_options:
                initial_dict[option.attribute_group.name] = option.name
            print(initial_dict)
            pass
        new_crop_form = NewCropForm(initial=initial_dict)
        return render(request, "inventory/new_crop.html",
                      context={"variety_list": variety_list, "barcode": new_crop_barcode, "new_crop_form": new_crop_form})

    if request.method == 'POST':
        form = NewCropForm(request.POST)
        print("Form is valid: ", form.is_valid())
        print(form.errors)
        if form.is_valid():
            variety = form.cleaned_data.pop('variety')
            germ_date = form.cleaned_data.pop('date_seeded')
            days_germinated = form.cleaned_data.pop('days_germinated')
            seeding_density = form.cleaned_data.pop('seeding_density')
            notes = form.cleaned_data.pop('notes')
            slot_barcode = request.POST["slot-barcode"]
            slot = get_object_or_404(Slot, barcode=slot_barcode)
            if slot.current_crop is not None:
                return HttpResponseBadRequest(f'Slot {slot.id} already contains a crop!')

            new_crop = Crop.objects.create(variety=variety, seeding_density=seeding_density, notes=notes)

            form_attributes = form.cleaned_data
            for attribute in form_attributes.keys():
                crop_attribute = CropAttribute.objects.get(name=attribute)
                option_name = form_attributes.get(attribute)
                crop_attribute_option = crop_attribute.options.get(name=option_name)
                new_crop.attributes.add(crop_attribute_option)

            slot.current_crop = new_crop
            slot.save()

            # Create a CropRecord to record when germination phase started
            CropRecord.objects.create(crop=new_crop, record_type='GERM', date=germ_date)
            # Create a CropRecord to record when germination phase started
            CropRecord.objects.create(crop=new_crop, record_type='GROW', date=(germ_date + timedelta(days_germinated)))

            # Redirect the user to the slot details page
            return redirect(slot_detail, slot_id=slot.id)

def edit_crop(request, crop_id):
    """GET: Display a form for editing crop data.
    POST: Accept form submission for editing crop data."""
    if request.method == 'GET':
        current_crop = get_object_or_404(Crop, id=crop_id)
        variety_list = Variety.objects.all()
        empty_slot_list = Slot.objects.filter(current_crop=None)
        # Try to find the slot holding this crop
        try:
            current_slot = Slot.objects.get(current_crop=current_crop)
            barcode = current_slot.barcode  # request.GET.get('barcode', current_slot.barcode)
        except Slot.DoesNotExist:
            current_slot = None
            barcode = None

        initial_dict = {}

        initial_dict['date_seeded'] = current_crop.germ_date()
        initial_dict['variety'] = current_crop.variety
        initial_dict['days_germinated'] = current_crop.days_in_germ()
        initial_dict['seeding_density'] = current_crop.seeding_density
        initial_dict['notes'] = current_crop.notes

        # Get the current crop's attributes to pre-populate form.
        crop_attribute_options = current_crop.attributes.all()
        print("crop attributes: ", crop_attribute_options)
        for option in crop_attribute_options:
            initial_dict[option.attribute_group.name] = option.name
        print(initial_dict)
        pass

        form = EditCropForm(initial=initial_dict)

        return render(request, "inventory/edit_crop.html",
                      context={"variety_list": variety_list, "barcode": barcode, "slot_list": empty_slot_list, "edit_crop_form": form})

    if request.method == 'POST':
        crop = get_object_or_404(Crop, id=crop_id)
        form = EditCropForm(request.POST)
        if form.is_valid():
            variety = form.cleaned_data.pop('variety')
            seeding_density = form.cleaned_data.pop('seeding_density')
            crop_notes = form.cleaned_data.pop('notes')
            slot_barcode = request.POST["slot-barcode"]
            slot = get_object_or_404(Slot, barcode=slot_barcode)
            if slot.current_crop is not None and slot.current_crop != crop:
                return HttpResponseBadRequest(f'Slot {slot.id} already contains a different crop!')
            # If the slot to move this crop to is empty
            elif slot.current_crop is None:
                # Remove crop from it's previous slot if exists
                if Slot.objects.filter(current_crop=crop).exists():
                    prev_slot = Slot.objects.filter(current_crop=crop)
                    prev_slot.current_crop = None
                    prev_slot.save()
                slot.current_crop = crop
                slot.save()


            # Edit the crop fields that aren't the CropAttributes
            crop.variety = variety
            crop.seeding_density = seeding_density
            crop.notes = crop_notes

            # Clear all the 'attributes'
            crop.attributes.clear()

            # Update crop 'attributes'
            for attribute in form.cleaned_data.keys():
                crop_attribute = CropAttribute.objects.get(name=attribute)
                option_name = form.cleaned_data.get(attribute)
                crop_attribute_option = crop_attribute.options.get(name=option_name)
                crop.attributes.add(crop_attribute_option)

            crop.save()
            return redirect(crop_detail, crop_id=crop.id)

@login_required
def add_crop_attributes(request):
    add_attributes_form = AddCropAttributesForm()
    add_attribute_options_form = AddAttributeOptionsForm()
    return render(request, "inventory/add_crop_attributes.html", context={"add_attributes_form": add_attributes_form, "add_attribute_options_form": add_attribute_options_form})


@login_required
def add_crop_attribute(request):
    form = AddCropAttributesForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        new_attribute = CropAttribute.objects.create(name=name)
        return add_crop_attributes(request)


@login_required
def add_attribute_option(request):
    form = AddAttributeOptionsForm(request.POST)
    if form.is_valid():
        options_name = form.cleaned_data['name']
        attribute_name = form.cleaned_data['attribute_group']
        attribute = CropAttribute.objects.get(name=attribute_name)
        new_options = CropAttributeOption.objects.create(name=options_name, attribute_group=attribute)
        return add_crop_attributes(request)


def get_crop_attributes_list(crop):
    if crop is None:
        return []
    else:
        attribute_options = crop.attributes.all()
        crop_attributes_list = []
        for option in attribute_options:
            option_name = option.name
            attribute_name = option.attribute_group.name
            crop_attributes_list.append((attribute_name, option_name))
        return crop_attributes_list

@login_required
def crop_detail(request, crop_id):
    """GET: Display the crop's details and history. The details include the type of crop, tray size,
    delivered live, ect. Page also provides a link to the crop's slot."""
    crop = Crop.objects.get(id=crop_id)
    edit = request.GET.get('edit', False)
    record_id = int(request.GET.get('id', -1))

    all_records = CropRecord.objects.filter(crop=crop_id)

    # FIXME -- handle this selection client-side via template filtering and selection
    try:
        seed = CropRecord.objects.filter(crop=crop_id).filter(record_type='SEED').order_by('-date')[0]
    except Exception:
        seed = None
    try:
        harvest = CropRecord.objects.filter(crop=crop_id).filter(record_type='HARVEST').order_by('-date')[0]
    except Exception:
        harvest = None
    try:
        trash = CropRecord.objects.filter(crop=crop_id).filter(record_type='TRASH').order_by('-date')[0]
    except Exception:
        trash = None

    record_types = [record[1] for record in CropRecord.RECORD_TYPES]  # This returns a list of all the readable crop record types
    crop_record_form = CropRecordForm(initial={'date': datetime.now().strftime("%m/%d/%Y")})
    notes_form = CropNotesForm(initial={'notes': crop.notes})
    crop_attributes = get_crop_attributes_list(crop)

    rack_channel_no = os.environ.get('RACK_CHANNEL_NO')
    germ_channel_no = os.environ.get('GERM_CHANNEL_NO')
    weather_channel_no = os.environ.get('WEATHER_CHANNEL_NO')
    rack_api_key = os.environ.get('RACK_API_KEY')
    germ_api_key = os.environ.get('GERM_API_KEY')
    weather_api_key = os.environ.get('WEATHER_API_KEY')

    return render(request, "inventory/crop_details.html", context={"history": all_records, "crop": crop, "crop_attributes": crop_attributes, "seed": seed,
                           "harvest": harvest, "trash": trash, "record_types": record_types, "edit": edit, "record_id": record_id,
                                                                   "crop_record_form": crop_record_form, "notes_form": notes_form, "rack_channel_no": rack_channel_no,
                                                                   "germ_channel_no": germ_channel_no, "rack_api_key": rack_api_key, "germ_api_key": germ_api_key,
                                                                   "weather_channel_no": weather_channel_no, "weather_api_key": weather_api_key})


@login_required
def record_crop_info(request, crop_id):
    """POST: Record a timestampped CropRecord event into the history of this crop's life."""
    form = CropRecordForm(request.POST)
    if form.is_valid():
        current_crop = Crop.objects.get(id=crop_id)
        record_type = form.cleaned_data["record_type"]
        record_date = form.cleaned_data["date"]
        new_crop_record = CropRecord.objects.create(crop=current_crop, record_type=record_type, date=record_date)
        return redirect(crop_detail, crop_id=current_crop.id)


@login_required
def slot_detail(request, slot_id):
    """GET: Displays the details of current crop in the slot and all the buttons used to control a tray in the greenhouse.
    Provides buttons and forms to perform tray actions.This is the page that people using the barcode scanner are going to
     see as they're working all day, so it needs to feel like a control panel."""
    slot = Slot.objects.get(id=slot_id)
    current_crop = slot.current_crop
    barcode = slot.barcode
    open_slots = Slot.objects.filter(current_crop=None)
    crop_attributes = get_crop_attributes_list(current_crop)
    all_records = CropRecord.objects.filter(crop=current_crop)
    try:
        water = CropRecord.objects.filter(crop=current_crop).filter(record_type='WATER').order_by('-date')[0]
    except Exception:
        water = None
    if current_crop:
        notes = current_crop.notes
    else:
        notes = ""
    notes_form = CropNotesForm(initial={'notes': notes})
    harvest_crop_form = HarvestCropForm()
    edit_crop_form = EditCropForm()
    return render(request, "inventory/slot_details.html", context={"slot_id": slot_id,
                                                                   "barcode": barcode,
                                                                   "crop": current_crop,
                                                                   "open_slots": open_slots,
                                                                   "crop_attributes": crop_attributes,
                                                                   "notes_form": notes_form,
                                                                   "harvest_crop_form": harvest_crop_form,
                                                                   "edit_crop_form": edit_crop_form,
                                                                   "water": water,
                                                                   "history": all_records })


@login_required
def slot_action():
    """GET: Display a form for a user to record an action on a tray.
    POST: Update the state of the Tray and make a CropRecord of whatever was done."""
    return None


@login_required
def harvest_crop(request, slot_id):
    """POST: Remove the crop from its tray, record crop history as harvest, and redirect to crop detail page."""
    form = HarvestCropForm(request.POST)
    if form.is_valid():
        # Update the data from the harvest crop form
        crop_yield = form.cleaned_data['crop_yield']
        leaf_wingspan = form.cleaned_data['leaf_wingspan']
        slot = Slot.objects.get(id=slot_id)
        current_crop = slot.current_crop
        current_crop.crop_yield = crop_yield
        current_crop.leaf_wingspan = leaf_wingspan
        current_crop.save()
        # Upload it to google sheets
        upload_data_to_sheets(current_crop)
        # Remove the crop from the slot
        slot.current_crop = None
        slot.save()
        # Add the harvest crop record
        CropRecord.objects.create(crop=current_crop, record_type="HARVEST")
        return redirect(crop_detail, crop_id=current_crop.id)


@login_required
def trash_crop(request, slot_id):
    """POST: Record that the crop has been trashed and redirect user to homepage."""
    reason_for_trash = request.POST["reason-for-trash-text"]
    slot = Slot.objects.get(id=slot_id)
    crop = slot.current_crop
    crop.notes = crop.notes + " TRASHED: " + reason_for_trash
    crop.save()
    upload_data_to_sheets(crop)
    slot.current_crop = None
    slot.save()
    CropRecord.objects.create(crop=crop, record_type='TRASH')
    return redirect(slot_detail, slot_id=slot_id)


@login_required
def water_crop(request, slot_id):
    """POST: Record that the crop has been watered and redirect user to homepage."""
    slot = Slot.objects.get(id=slot_id)
    crop = slot.current_crop
    rec = CropRecord.objects.create(crop=crop, record_type='WATER', date=date.today())
    return redirect(slot_detail, slot_id=slot_id)

@login_required
def search_crop(request):
    """GET: Go to the crop page based on the input of crop id or barcode"""
    search_method = request.GET.get('search-method')
    if search_method == 'form-search-by-id':
        crop_id = request.GET.get('form-search-crop-id-or-barcode')
        crop = get_object_or_404(Crop, id=crop_id)
    elif search_method == 'form-search-by-barcode':
        barcode = request.GET.get('form-search-crop-id-or-barcode')
        slot = get_object_or_404(Slot, barcode=barcode)
        crop = get_object_or_404(Crop, current_slot=slot)

    return redirect(crop_detail, crop_id=crop.id)

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
    date_object = parser.parse(updated_date)
    crop_record.date = date_object
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
        form = SanitationRecordForm(initial={'date': datetime.now().strftime("%m/%d/%Y") })
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
        try:
            CropGroup.objects.create(variety=v, quantity=0, seed_date=datetime.today)
        except:
            pass
    in_house = []
    for variety in Variety.objects.all():
        total_trays = 0
        for crop_group in CropGroup.objects.filter(variety=variety):
            total_trays += crop_group.quantity
        in_house.append((variety, total_trays))

    return render(request, 'inventory/inventory_overview.html', context={'in_house': in_house})

@login_required
def inventory_seed(request):
    if request.method == 'GET':
        day = date.today()
        variety_list = []
        for v in Variety.objects.all():
            if len(WeekdayRequirement.objects.filter(plant_day=day.weekday()).filter(variety=v)) == 0:
                WeekdayRequirement.objects.create(variety=v, plant_day=day.weekday(), quantity=0)
            variety_name_no_spaces = v.name.replace(" ", "-").replace(":", "").replace(",", "")
            variety_list.append((v, variety_name_no_spaces))
        return render(request, 'inventory/inventory_seed.html', context={'variety_list': variety_list, 'day': day.isoformat()})
    
    if request.method == 'POST':
        try:
            # Try to get the date from the form
            seed_date = parser.parse(request.POST.get('day'))
        except TypeError:
            seed_date = datetime.today()
            pass
        for v in Variety.objects.all():
            try:
                quantity = request.POST['form-plan-' + v.name.replace(" ", "-").replace(":", "").replace(",", "") + '-quantity']
                quantity = 0 if len(quantity) == 0 else int(quantity)
                try:
                    in_house = CropGroup.objects.get(variety=v, seed_date=seed_date)
                except CropGroup.DoesNotExist:
                    in_house = CropGroup.objects.create(variety=v, seed_date=seed_date)
                in_house.quantity += quantity
                in_house.save()
                if quantity:
                    data = json.dumps({'quantity': quantity})
                    var_obj = Variety.objects.get(name=v)
                    InventoryAction.objects.create(variety=var_obj, date=seed_date, action_type='SEED', data=data)
            except KeyError:
                pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@login_required
def inventory_kill(request):
    if request.method == 'GET':
        day = date.today()
        return render(request, 'inventory/inventory_kill.html', context={'variety_list':Variety.objects.all(), 'reason_list':KillReason.objects.all(), 'day':day.isoformat()})
    
    if request.method == 'POST':
        try:
            variety = request.POST['form-kill-variety']
            quantity = request.POST['form-kill-quantity']
            day = parser.parse(request.POST['form-kill-date'])
            date_seeded = parser.parse(request.POST['form-kill-seed-date'])
            quantity = 0 if len(quantity) == 0 else int(quantity)
            reason = request.POST['form-kill-reason']
            var_obj = Variety.objects.get(name=variety)
            reason_obj = KillReason.objects.get(name=reason)
            try:
                in_house = CropGroup.objects.get(variety=var_obj, seed_date=date_seeded)
                in_house.quantity = in_house.quantity - quantity if quantity <= in_house.quantity else 0
                in_house.save()
                if quantity:
                    data = json.dumps({'quantity': quantity})
                    InventoryAction.objects.create(variety=var_obj, action_type='KILL', date=day,
                                                   kill_reason=reason_obj, data=data)
            except CropGroup.DoesNotExist:
                pass
        except KeyError as e:
            print (e)
            pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@login_required
def inventory_plan(request, plant_day=None):
    if plant_day == None:
        plant_day = datetime.today().weekday()
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    if request.method == 'GET':
        variety_list = []
        for v in Variety.objects.all():
            if len(WeekdayRequirement.objects.filter(plant_day=plant_day).filter(variety=v)) == 0:
                WeekdayRequirement.objects.create(variety=v, plant_day=plant_day, quantity=0)
            variety_name_no_spaces = v.name.replace(" ", "-").replace(":", "").replace(",", "")
            variety_list.append((v, variety_name_no_spaces))
        return render(request, 'inventory/inventory_recurring.html', context={'day': plant_day, 'weekdays': DAYS_OF_WEEK, 'variety_list': variety_list})
    
    if request.method == 'POST':
        print(str(request.POST))
        variety_list = []
        for v in Variety.objects.all():
            try:
                day = int(request.POST['day'])
                quantity = int(request.POST['form-plan-' + v.name.replace(" ", "-").replace(":","").replace(",", "") + '-quantity'])
                plan = WeekdayRequirement.objects.get(variety=v, plant_day=day)
                plan.quantity = quantity
                plan.save()
                variety_name_no_spaces = v.name.replace(" ", "-").replace(":", "").replace(",", "")
                variety_list.append((v, variety_name_no_spaces))
            except KeyError:
                pass # In case there's a variety inconsistency
        # Redirect the user to the weekly planning page
        return render(request, 'inventory/inventory_recurring.html', context={'day': day, 'weekdays': DAYS_OF_WEEK, 'variety_list': variety_list})

@login_required
def inventory_harvest_bulk(request): # numbers of trays for multiple varieties
    today = date.today().isoformat()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_harvest_bulk.html', context={'variety_list':Variety.objects.all(), 'today':today})
    
    if request.method == 'POST':
        for v in Variety.objects.all():
            try:
                h_date = request.POST['form-harvest-date']
                to_harvest = request.POST['form-harvest-' + v.name + '-quantity']
                seed_date = request.POST['form-harvest-' + v.name + '-seed-date']
                # TODO: Give error message if date was not given
                # If a harvest number was given
                if len(to_harvest) != 0:
                    to_harvest = int(to_harvest)
                    # If seed date was given
                    if len(seed_date) != 0:
                        # Update the CropGroup size
                        in_house = CropGroup.objects.get(variety=v, seed_date=seed_date)
                        in_house.quantity = in_house.quantity - to_harvest if to_harvest <= in_house.quantity else 0
                        in_house.save()
                        # Create InventoryAction
                        if to_harvest:
                            data = json.dumps({'num_harvested': to_harvest})
                            InventoryAction.objects.create(variety=v, date=h_date, action_type='HARVEST', data=data)
                    # If seed_date was not given, throw error
                    elif len(seed_date) == 0:
                        raise ValidationError("A seed date must be provided!")
                    # If harvest number was not given, skip this
            except KeyError:
                pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@login_required
def inventory_harvest_variety(request): # Numbers of trays and yield for a single variety
    today = date.today().isoformat()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_harvest_variety.html', context={'variety_list':Variety.objects.all(), 'today':today})
    
    if request.method == 'POST':
        try:
            variety = request.POST['form-harvest-variety']
            h_date = request.POST['form-harvest-date']
            to_harvest = request.POST['form-harvest-quantity']
            h_yield = request.POST['form-harvest-yield']
            seed_date = request.POST['form-harvest-seed-date']
            to_harvest = 0 if len(to_harvest) == 0 else int(to_harvest)
            h_yield = 0 if len(h_yield) == 0 else float(h_yield)
            var_obj = Variety.objects.get(name=variety)
            in_house = CropGroup.objects.get(variety=var_obj, seed_date=seed_date)
            in_house.quantity = in_house.quantity - to_harvest if to_harvest <= in_house.quantity else 0
            in_house.save()
            if to_harvest:
                data = json.dumps({'num_harvested': to_harvest, 'yield': h_yield})
                InventoryAction.objects.create(variety=var_obj, action_type='HARVEST', data=data, date=h_date)
        except KeyError as e:
            print (e)
            pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@login_required
def inventory_harvest_single(request): # One tray, with detailed records
    today = date.today().isoformat()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_harvest_single.html', context={'variety_list':Variety.objects.all(), 'today':today})
    
    if request.method == 'POST':
        try:
            h_date = request.POST['form-harvest-date']
            variety = request.POST['form-harvest-variety']
            seed_date = request.POST['form-harvest-seed-date']
            h_yield = request.POST['form-harvest-yield']
            h_yield = 0 if len(h_yield) == 0 else float(h_yield)
            var_obj = Variety.objects.get(name=variety)
            in_house = CropGroup.objects.get(variety=var_obj, seed_date=seed_date)
            in_house.quantity = in_house.quantity - 1 if 1 <= in_house.quantity else 0
            in_house.save()
            data = json.dumps({'num_harvested': 1, 'yield': h_yield})
            InventoryAction.objects.create(variety=var_obj, action_type='HARVEST', data=data, date=h_date)
        except KeyError as e:
            print (e)
            pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)


@login_required
def weekday_autofill(request):
    day = request.GET.get('day', None)
    # check if day is not already weekday number
    if day not in ["0", "1", "2", "3", "4", "5", "6"]:
        day = parser.parse(day).weekday()
    data = {}
    for v in Variety.objects.all():
        if len(WeekdayRequirement.objects.filter(plant_day=day).filter(variety=v)) == 0:
            WeekdayRequirement.objects.create(variety=v, plant_day=day, quantity=0)
        try:
            plan = WeekdayRequirement.objects.get(variety=v, plant_day=day)
            data[v.name + '-quantity'] = plan.quantity
        except Exception as e:
            print (e)
            pass
    return JsonResponse(data)

@login_required
def environment_data(request):
    """GET: Display a page that shows temperature and humidity data from the farm."""
    rack_channel_no = os.environ.get('RACK_CHANNEL_NO')
    germ_channel_no = os.environ.get('GERM_CHANNEL_NO')
    weather_channel_no = os.environ.get('WEATHER_CHANNEL_NO')
    rack_api_key = os.environ.get('RACK_API_KEY')
    germ_api_key = os.environ.get('GERM_API_KEY')
    weather_api_key = os.environ.get('WEATHER_API_KEY')

    return render(request, "inventory/environment_data.html", context={"rack_channel_no": rack_channel_no, "germ_channel_no": germ_channel_no, "rack_api_key": rack_api_key, "germ_api_key": germ_api_key, "weather_channel_no": weather_channel_no, "weather_api_key": weather_api_key})

@login_required
def add_barcodes(request):
    """GET: All slots """
    if request.method == 'GET':
        slot_list = Slot.objects.all()
        initial_dict = {}
        for slot in slot_list:
            initial_dict["Slot " + str(slot.id)] = slot.barcode
        form = AddBarcodesForm(initial=initial_dict)
        return render(request, "inventory/add_barcodes.html",
                      context={"slot_list": slot_list,
                               "add_barcodes_to_slots_form": form})
    if request.method == 'POST':
        slot_list = Slot.objects.all()
        form = AddBarcodesForm(request.POST)
        if form.is_valid():
            # form.cleaned_data = form.clean_barcode()
            for slot in slot_list:
                slot.barcode = form.cleaned_data.pop('Slot '+str(slot.id))
                slot.save()
        return redirect(golden_trays_home)