from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from inventory.models import WeekdayRequirement, InventoryAction, CropGroup, LiveCropInventory
from inventory.forms import *
from orders.models import LiveCropProduct, MicrogreenSize, TrayType, Product, HarvestedCropProduct
from orders.views import orders_home
from datetime import date, datetime, timedelta
from dateutil import parser
from google_sheets.upload_to_sheet import upload_data_to_sheets
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
import os
import json
# Crop, CropAttribute, CropAttributeOption, CropRecord, Slot, Variety,


@staff_member_required
def golden_trays_home(request):
    """GET: Display the homepage for the golden trays"""
    return render(request, "inventory/golden_trays_home.html")

@login_required
def homepage(request):
    """GET: Display inventory home page if user is staff, else display customer view homepage."""
    total_slot_count = Slot.objects.count()
    if request.user.is_staff:
        return render(request, "inventory/index.html", context={"total_slot_count": total_slot_count})
    return redirect(orders_home)

@staff_member_required
def growhouse_settings(request):
    """GET: Shows the setup page which contains forms for the inital setup of the grow space including
    allowing a user to set the original number of slots and adding varieties"""
    total_slot_count = Slot.objects.count()
    free_slot_count = Slot.objects.filter(current_crop__isnull=True).count()
    add_variety_form = AddVarietyForm()
    return render(request, "inventory/growhouse_settings.html", context={"total_slot_count": total_slot_count, "free_slot_count": free_slot_count, "form": add_variety_form})

@staff_member_required
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


@staff_member_required
def add_variety(request):
    """POST: Adds Variety Objects"""
    form = AddVarietyForm(request.POST)
    if form.is_valid():
        variety_name = form.cleaned_data["name"]
        Variety.objects.create(name=variety_name)

        return redirect(growhouse_settings)

    total_slot_count = Slot.objects.count()
    return render(request, "inventory/growhouse_settings.html", context={"total_slot_count": total_slot_count, "form": form})

@staff_member_required
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


@staff_member_required
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

@staff_member_required
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

@staff_member_required
def add_crop_attributes(request):
    add_attributes_form = AddCropAttributesForm()
    add_attribute_options_form = AddAttributeOptionsForm()
    return render(request, "inventory/add_crop_attributes.html", context={"add_attributes_form": add_attributes_form, "add_attribute_options_form": add_attribute_options_form})


@staff_member_required
def add_crop_attribute(request):
    form = AddCropAttributesForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        new_attribute = CropAttribute.objects.create(name=name)
        return add_crop_attributes(request)


@staff_member_required
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

@staff_member_required
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


@staff_member_required
def record_crop_info(request, crop_id):
    """POST: Record a timestampped CropRecord event into the history of this crop's life."""
    form = CropRecordForm(request.POST)
    if form.is_valid():
        current_crop = Crop.objects.get(id=crop_id)
        record_type = form.cleaned_data["record_type"]
        record_date = form.cleaned_data["date"]
        new_crop_record = CropRecord.objects.create(crop=current_crop, record_type=record_type, date=record_date)
        return redirect(crop_detail, crop_id=current_crop.id)


@staff_member_required
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


@staff_member_required
def slot_action():
    """GET: Display a form for a user to record an action on a tray.
    POST: Update the state of the Tray and make a CropRecord of whatever was done."""
    return None


@staff_member_required
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


@staff_member_required
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


@staff_member_required
def water_crop(request, slot_id):
    """POST: Record that the crop has been watered and redirect user to homepage."""
    slot = Slot.objects.get(id=slot_id)
    crop = slot.current_crop
    rec = CropRecord.objects.create(crop=crop, record_type='WATER', date=date.today())
    return redirect(slot_detail, slot_id=slot_id)

@staff_member_required
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

@staff_member_required
def delete_record(request, record_id):
    """GET: Deletes the crop record with the specified record id"""
    crop_record = CropRecord.objects.get(id=record_id)
    crop_record.delete()
    crop = crop_record.crop
    return redirect(crop_detail, crop_id=crop.id)

@staff_member_required
def update_crop_record(request, record_id):
    """POST: Updates the specified record"""
    crop_record = CropRecord.objects.get(id=record_id)
    updated_date = request.POST["date"]
    date_object = parser.parse(updated_date)
    crop_record.date = date_object
    crop_record.save()
    crop = crop_record.crop
    return redirect(crop_detail, crop_id=crop.id)

@staff_member_required
def parse_barcode(request, barcode_text):
    slot = get_object_or_404(Slot, barcode=barcode_text)
    return redirect(slot_detail, slot_id=slot.id)

@staff_member_required
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


@staff_member_required
def variety_autofill(request):
    variety = request.GET.get('variety', None)
    data = {
        'days_germ': Variety.objects.get(name=variety).days_germ,
        'days_grow': Variety.objects.get(name=variety).days_grow
    }
    return JsonResponse(data)

@staff_member_required
def inventory_home(request):
    return render(request, "inventory/inventory_home.html")

@staff_member_required
def inventory_overview(request):
    in_house = {}
    variety_list = []
    for variety in Variety.objects.all().order_by('name'):
        crop_groups = []
        in_house[variety.name] = {}
        variety_list.append(variety.name)
        variety_alphanumeric = variety.name.replace(" ", "-").replace(":", "").replace(",", "")
        total_trays = 0
        for crop_group in CropGroup.objects.filter(variety=variety).exclude(quantity=0).order_by('seed_date'):
            crop_groups.append(crop_group)
            total_trays += crop_group.quantity
        in_house[variety.name]['total_trays'] = total_trays
        in_house[variety.name]['name'] = variety.name
        in_house[variety.name]['name_alphanumeric'] = variety_alphanumeric
        in_house[variety.name]['crop_groups'] = crop_groups

    # Date range breakdown [d1, d2, ... dn]
    # Break into dn+1 groups of crops < di days old
    # eg. [0, 4 d/o), [4, 14 d/o), [14, inf d/o)
    breakdown = [10, 20, 30]
    colors = ['#70ef94', '#efdc70', '#f4a802', '#f43a02'] # getChartColors((0, 255, 0), (255, 0, 0) ,len(breakdown) + 1)
    chart_series = []
    start_date = date.today()
    for x in range(0, len(breakdown) + 1):
        data = []
        category_dict = {}
        if x != len(breakdown):
            end_date = start_date # set end date to previous start date
            start_date = date.today() - timedelta(days=breakdown[x]-1)
            category_dict['name'] = "< " + str(breakdown[x]) + " days"
        else:
            end_date = start_date
            category_dict = {'name': str(breakdown[len(breakdown) - 1]) + "+ days", 'data': []}
        for v in Variety.objects.all().order_by('name'):
            count = 0
            if x == len(breakdown):
                for cg in CropGroup.objects.filter(variety=v, seed_date__lte=end_date):
                    count += cg.quantity
            else:
                for cg in CropGroup.objects.filter(variety=v, seed_date__range=[start_date, end_date]):
                    count += cg.quantity
            data.append(count)
        category_dict['data'] = data
        chart_series.append(category_dict)
    # Recent Inventory Actions
    recent_actions = InventoryAction.objects.all().order_by('-date')[:5]
    actions_display = []
    for action in recent_actions:
        if action.action_type == 'SEED':
            text = "Seeded: " + str(action.quantity) + " trays of " + action.variety.name + "."
        if action.action_type == 'HARVEST':
            text = "Harvested: " + str(action.quantity) + " trays of " + action.variety.name + "."
        if action.action_type == 'KILL':
            reasons = ", ".join(list(action.kill_reasons.values_list('name', flat=True)))
            print(reasons)
            text = "Killed: " + str(action.quantity) + " trays of " + action.variety.name + " because of " + reasons + "."
        actions_display.append((action, text))

    return render(request, 'inventory/inventory_overview.html', context={'in_house': in_house,
                                                                         'chart_series': chart_series,
                                                                         'variety_list': variety_list,
                                                                         'chart_colors': colors,
                                                                         'recent_actions': actions_display})


# One-time function to make all LiveCropInventories from LiveCropProducts
def make_live_crop_inventory():
    for lcp in LiveCropProduct.objects.all():
        LiveCropInventory.objects.create(product=lcp, quantity=0)


# Interpolate between start and end color (rgb tuples) with n increments and return a list of hex colors
def getChartColors(start_color, end_color, n):
    colors = []
    red_init = start_color[0]
    green_init = start_color[1]
    blue_init = start_color[2]
    red_final = end_color[0]
    green_final = end_color[1]
    blue_final = end_color[2]
    for i in range(0, n):
        red = red_init + int(((red_final - red_init) / n) * i)
        green = green_init + int(((green_final - green_init) / n) * i)
        blue = blue_init + int(((blue_final - blue_init) / n) * i)
        colors.append("#{0:02x}{1:02x}{2:02x}".format(red, green, blue))
    return colors

@staff_member_required
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
                if quantity:
                    try:
                        in_house = CropGroup.objects.get(variety=v, seed_date=seed_date)
                    except CropGroup.DoesNotExist:
                        in_house = CropGroup.objects.create(variety=v, seed_date=seed_date)
                    in_house.quantity += quantity
                    in_house.save()
                    # data = json.dumps({'quantity': quantity})
                    var_obj = Variety.objects.get(name=v)
                    InventoryAction.objects.create(variety=var_obj, date=seed_date, action_type='SEED', quantity=quantity)
            except KeyError:
                pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@staff_member_required
def inventory_kill(request):
    if request.method == 'GET':
        day = date.today()
        return render(request, 'inventory/inventory_kill.html', context={'variety_list': Variety.objects.all().order_by('name'), 'reason_list':KillReason.objects.all(), 'day':day.isoformat()})
    
    if request.method == 'POST':
        try:
            variety = request.POST['form-kill-variety']
            var_obj = Variety.objects.get(name=variety)
            quantity = request.POST['form-kill-quantity']
            day = request.POST['form-kill-date']
            date_seeded = request.POST['form-kill-seed-date']
            reasons = []
            for kill_reason in KillReason.objects.all():
                if request.POST.get(kill_reason.name + '-checkbox') == 'on':
                    reasons.append(kill_reason)
            if len(quantity) != 0 and int(quantity) > 0:
                quantity = int(quantity)
                try:
                    in_house = CropGroup.objects.get(variety=var_obj, seed_date=date_seeded)
                    if quantity <= in_house.quantity:
                        in_house.quantity = in_house.quantity - quantity
                        in_house.save()
                        inventory_action = InventoryAction.objects.create(variety=var_obj, action_type='KILL',
                                                                          date=day, quantity=quantity)
                        for kill_reason in reasons:
                            inventory_action.kill_reasons.add(kill_reason)
                        inventory_action.save()
                    else:
                        message = "There are only " + str(in_house.quantity) + " " + variety + "s for " \
                                  + date_seeded \
                                  + " in your database and you were trying to harvest " + str(quantity) \
                                  + ". Check your "
                        return render(request, 'inventory/inventory_kill.html',
                                      context={'variety_list': Variety.objects.all().order_by('name'),
                                               'reason_list': KillReason.objects.all(), 'day': day,
                                               'date_seeded': date_seeded, 'quantity': quantity,
                                               'selected_variety': variety,
                                               'selected_reasons': reasons, 'error': message})
                except CropGroup.DoesNotExist:
                    message = "The crop(s) you were trying to kill don't exist in your database. Check your "
                    return render(request, 'inventory/inventory_kill.html', context={'variety_list': Variety.objects.all().order_by('name'),
                                                                                     'reason_list': KillReason.objects.all(),
                                                                                     'day': day, 'date_seeded': date_seeded,
                                                                                     'quantity': quantity,
                                                                                     'selected_variety': variety,
                                                                                     'selected_reasons': reasons,
                                                                                    'error': message})
            else:
                message = "Please enter a positive, non-zero quantity. Check your "
                return render(request, 'inventory/inventory_kill.html', context={'variety_list': Variety.objects.all().order_by('name'),
                                                                                 'reason_list': KillReason.objects.all(),
                                                                                 'day': day, 'date_seeded': date_seeded,
                                                                                 'quantity': quantity,
                                                                                 'selected_variety': variety,
                                                                                 'selected_reasons': reasons,
                                                                                 'error': message})
        except KeyError as e:
            print (e)
            pass # In case there's a variety inconsistency

        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@staff_member_required
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

@staff_member_required
def inventory_harvest_bulk(request): # numbers of trays for multiple varieties
    today = date.today().isoformat()
    if request.method == 'GET':
        variety_list = []
        for v in Variety.objects.all().order_by('name'):
            variety_list.append({'name': v.name, 'quantity': None, 'date': None})
        return render(request, 'inventory/inventory_harvest_bulk.html', context={'variety_list': variety_list, 'date':today})
    
    if request.method == 'POST':
        # Save the current state of the form in case of error later on
        variety_list = []
        for v in Variety.objects.all().order_by('name'):
            try:
                quantity = request.POST['form-harvest-' + v.name + '-quantity']
                seed_date = request.POST['form-harvest-' + v.name + '-seed-date']
                variety_list.append({'name': v.name, 'quantity': quantity, 'date': seed_date})
            except KeyError:
                pass  # In case there's a variety inconsistency

        for v in Variety.objects.all().order_by('name'):
            try:
                h_date = request.POST['form-harvest-date']
                quantity = request.POST['form-harvest-' + v.name + '-quantity']
                seed_date = request.POST['form-harvest-' + v.name + '-seed-date']
                # If a harvest quantity was given and its not zero
                if len(quantity) != 0 and int(quantity) > 0 and len(seed_date) != 0:
                    quantity = int(quantity)
                    try:
                        # Update the CropGroup size
                        in_house = CropGroup.objects.get(variety=v, seed_date=seed_date)
                        if quantity <= in_house.quantity:
                            in_house.quantity = in_house.quantity - quantity if quantity <= in_house.quantity else 0
                            in_house.save()
                            # Create InventoryAction, only if quantity != 0
                            InventoryAction.objects.create(variety=v, date=h_date, action_type='HARVEST', quantity=quantity)
                        else:
                            message = "There are only " + str(in_house.quantity) + " " + v.name + "s for " + seed_date \
                                      + " in your database and you were trying to harvest " + str(quantity) \
                                      + ". Check your "
                            return render(request, 'inventory/inventory_harvest_bulk.html',
                                          context={'variety_list': variety_list, 'date': h_date,
                                                   'error': message})
                    except CropGroup.DoesNotExist:
                        message = "The crop(s) you were trying to harvest don't exist in your database. Check your "
                        return render(request, 'inventory/inventory_harvest_bulk.html',
                                      context={'variety_list': variety_list, 'date': h_date, 'error': message})

                # If seed_date was not given, throw error
                elif len(quantity) != 0 and int(quantity) > 0 and len(seed_date) == 0:
                    message = "A seed date must be provided for " + v.name + ". Check your "
                    return render(request, 'inventory/inventory_harvest_bulk.html',
                                  context={'variety_list': variety_list, 'date': h_date, 'error': message})
            except KeyError:
                pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@staff_member_required
def inventory_harvest_variety(request): # Numbers of trays and yield for a single variety
    today = date.today().isoformat()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_harvest_variety.html', context={'variety_list':Variety.objects.all().order_by('name'), 'date':today})
    
    if request.method == 'POST':
        try:
            variety = request.POST['form-harvest-variety']
            h_date = request.POST['form-harvest-date']
            quantity = request.POST['form-harvest-quantity']
            h_yield = request.POST['form-harvest-yield']
            seed_date = request.POST['form-harvest-seed-date']
            h_yield = 0 if len(h_yield) == 0 else float(h_yield)
            var_obj = Variety.objects.get(name=variety)
            if len(quantity) != 0 and int(quantity) > 0:
                quantity = int(quantity)
                try:
                    in_house = CropGroup.objects.get(variety=var_obj, seed_date=seed_date)
                    if quantity <= in_house.quantity:
                        in_house.quantity = in_house.quantity - quantity
                        in_house.save()
                        if quantity:
                            InventoryAction.objects.create(variety=var_obj, action_type='HARVEST', quantity=quantity, date=h_date)
                    else:
                        message = "There are only " + str(in_house.quantity) + " " + variety + "s for " + seed_date \
                                  + " in your database and you were trying to harvest " + str(quantity) + ". Check your "
                        return render(request, 'inventory/inventory_harvest_variety.html',
                                      context={'variety_list': Variety.objects.all().order_by('name'), 'date': h_date,
                                               'seed_date': seed_date, 'yield': h_yield, 'quantity': quantity,
                                               'selected_variety': variety, 'error': message})
                except CropGroup.DoesNotExist:
                    message = "The crop(s) you were trying to harvest don't exist in your database. Check your "
                    return render(request, 'inventory/inventory_harvest_variety.html',
                                  context={'variety_list': Variety.objects.all().order_by('name'), 'date': h_date,
                                           'seed_date': seed_date, 'yield': h_yield, 'quantity': quantity,
                                           'selected_variety': variety, 'error': message})
            else:
                message = "Please enter a positive, non-zero quantity. Check your "
                return render(request, 'inventory/inventory_harvest_variety.html',
                              context={'variety_list': Variety.objects.all().order_by('name'), 'date': h_date, 'seed_date': seed_date,
                                       'yield': h_yield, 'quantity': quantity,  'selected_variety': variety, 'error': message})
        except KeyError as e:
            print (e)
            pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@staff_member_required
def inventory_harvest_single(request): # One tray, with detailed records
    today = date.today().isoformat()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_harvest_single.html', context={'variety_list':Variety.objects.all().order_by('name'), 'today':today})
    
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
            # data = json.dumps({'quantity': 1, 'yield': h_yield})
            InventoryAction.objects.create(variety=var_obj, action_type='HARVEST', quantity=1, date=h_date)
        except KeyError as e:
            print (e)
            pass # In case there's a variety inconsistency
        
        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)

@staff_member_required
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

@staff_member_required
def environment_data(request):
    """GET: Display a page that shows temperature and humidity data from the farm."""
    rack_channel_no = os.environ.get('RACK_CHANNEL_NO')
    germ_channel_no = os.environ.get('GERM_CHANNEL_NO')
    weather_channel_no = os.environ.get('WEATHER_CHANNEL_NO')
    rack_api_key = os.environ.get('RACK_API_KEY')
    germ_api_key = os.environ.get('GERM_API_KEY')
    weather_api_key = os.environ.get('WEATHER_API_KEY')

    return render(request, "inventory/environment_data.html", context={"rack_channel_no": rack_channel_no, "germ_channel_no": germ_channel_no, "rack_api_key": rack_api_key, "germ_api_key": germ_api_key, "weather_channel_no": weather_channel_no, "weather_api_key": weather_api_key})

@staff_member_required
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


@staff_member_required
def add_product(request):
    if request.method == 'GET':
        variety_list = []
        for v in Variety.objects.all().order_by('name'):
            variety_list.append(v.name)
        sizes = []
        for s in MicrogreenSize.objects.all().order_by('name'):
            sizes.append(s.name)
        tray_types = []
        for t in TrayType.objects.all().order_by('name'):
            tray_types.append(t.name)
        product_form = AddProductForm()
        return render(request, "inventory/add_product.html", context={"product_form": product_form,
                                                                      "varieties": variety_list,
                                                                      "tray_types": tray_types,
                                                                      "sizes": sizes})
    if request.method == 'POST':
        variety_list = []
        for v in Variety.objects.all().order_by('name'):
            variety_list.append(v.name)
        sizes = []
        for s in MicrogreenSize.objects.all().order_by('name'):
            sizes.append(s.name)
        tray_types = []
        for t in TrayType.objects.all().order_by('name'):
            tray_types.append(t.name)
        product_form = AddProductForm()
        form = AddProductForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            fields = request.POST
            product_name = fields['product_name']
            price = fields['price']
            try:
                if fields['select-product-type'] == 'Live Crop Product':
                    print("Live crop product!")
                    variety = Variety.objects.get(name=fields['variety'])
                    size = MicrogreenSize.objects.get(name=fields['size'])
                    tray_type = TrayType.objects.get(name=fields['tray-type'])
                    LiveCropProduct.objects.create(name=product_name, price=price, variety=variety,
                                                   size=size, tray_type=tray_type)
                elif fields['select-product-type'] == 'Harvested Crop Product':
                    variety = Variety.objects.get(name=fields['variety'])
                    size = MicrogreenSize.objects.get(name=fields['size'])
                    weight = int(fields['weight'])
                    HarvestedCropProduct.objects.create(name=product_name, price=price, variety=variety,
                                                   size=size, weight=weight)
            except KeyError:
                Product.objects.create(name=product_name, price=price)
                pass
            message = "Successfully added " + product_name + " to your "
            # TODO: option to pre-fill previous form's values
            return render(request, "inventory/add_product.html", context={"product_form": product_form,
                                                                          "varieties": variety_list,
                                                                          "tray_types": tray_types,
                                                                          "sizes": sizes,
                                                                          "success": message})
        else:
            message = "Something went wrong."
            print(message)
            return render(request, "inventory/add_product.html", context={"product_form": product_form,
                                                                          "varieties": variety_list,
                                                                          "tray_types": tray_types,
                                                                          "sizes": sizes,
                                                                          "error": message})

@staff_member_required
def catalog(request):
    if request.method == 'GET':
        other_products = []
        for product in Product.objects.all():
            if not LiveCropProduct.objects.filter(id=product.id).exists() \
                    and not HarvestedCropProduct.objects.filter(id=product.id).exists():
                other_products.append(product)
        return render(request, "inventory/catalog.html", context={"live_crop_products": LiveCropProduct.objects.all(),
                                                                  "harvested_crop_products": HarvestedCropProduct.objects.all(),
                                                                  "other_products": other_products})
    # if request.method == 'POST':
    #     live_crop_products = []
    #     harvested_crop_products = []
    #     other_products = []
    #     return render(request, "inventory/catalog.html", context={"live_crop_products": live_crop_products,
    #                                                               "harvested_crop_products": harvested_crop_products,
    #                                                               "other_products": other_products})