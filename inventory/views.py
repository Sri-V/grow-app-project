from django.http import JsonResponse
from django.shortcuts import redirect, render
from inventory.models import WeekdayRequirement, InventoryAction, CropGroup, LiveCropInventory
from inventory.forms import *
from golden_trays.forms import *
from orders.models import LiveCropProduct, MicrogreenSize, TrayType, Product, HarvestedCropProduct
from datetime import date, datetime, timedelta
from dateutil import parser
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
import os



@login_required
def homepage(request):
    """GET: Display a homepage that offers links to inventory, golden trays and environmental data"""
    return render(request, "inventory/index.html")


@staff_member_required
def growhouse_settings(request):
    """GET: Shows the setup page which contains forms for the inital setup of the grow space including
    allowing a user to set the original number of slots and adding varieties"""
    total_slot_count = Slot.objects.count()
    free_slot_count = Slot.objects.filter(current_crop__isnull=True).count()
    add_variety_form = AddVarietyForm()
    return render(request, "inventory/growhouse_settings.html",
                  context={"total_slot_count": total_slot_count, "free_slot_count": free_slot_count,
                           "form": add_variety_form})


@staff_member_required
def set_total_slot_quantity(request):
    """POST: Update the number of total Slot objects, redirect to homepage."""
    phase = "G"  # Phase will always be grow since we are on tracking golden trays in grow
    racks = int(request.POST["racks"])
    rows = int(request.POST["rows"])
    slots = int(request.POST["slots"])
    # current_slot_count = Slot.objects.count()
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
    return render(request, "inventory/growhouse_settings.html",
                  context={"total_slot_count": total_slot_count, "form": form})



@staff_member_required
def sanitation_records(request):
    """GET: Displays the page with the current sanitation records
    POST: Records the new sanitation record"""
    if request.method == 'GET':
        sanitation_record_list = SanitationRecord.objects.all().order_by('-date')
        form = SanitationRecordForm(initial={'date': datetime.now().strftime("%m/%d/%Y")})
        return render(request, "inventory/sanitation_records.html",
                      context={"record_list": sanitation_record_list, "form": form})

    if request.method == 'POST':
        form = SanitationRecordForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            employee_name = form.cleaned_data['employee_name']
            equipment_sanitized = form.cleaned_data['equipment_sanitized']
            chemicals_used = form.cleaned_data['chemicals_used']
            note = form.cleaned_data['note']

            SanitationRecord.objects.create(date=date, employee_name=employee_name,
                                            equipment_sanitized=equipment_sanitized, chemicals_used=chemicals_used,
                                            note=note)

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
    colors = ['#70ef94', '#efdc70', '#f4a802',
              '#f43a02']  # getChartColors((0, 255, 0), (255, 0, 0) ,len(breakdown) + 1)
    chart_series = []
    start_date = date.today()
    for x in range(0, len(breakdown) + 1):
        data = []
        category_dict = {}
        if x != len(breakdown):
            end_date = start_date  # set end date to previous start date
            start_date = date.today() - timedelta(days=breakdown[x] - 1)
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
            text = "Killed: " + str(
                action.quantity) + " trays of " + action.variety.name + " because of " + reasons + "."
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
        return render(request, 'inventory/inventory_seed.html',
                      context={'variety_list': variety_list, 'day': day.isoformat()})

    if request.method == 'POST':
        try:
            # Try to get the date from the form
            seed_date = parser.parse(request.POST.get('day'))
        except TypeError:
            seed_date = datetime.today()
            pass
        for v in Variety.objects.all():
            try:
                quantity = request.POST[
                    'form-plan-' + v.name.replace(" ", "-").replace(":", "").replace(",", "") + '-quantity']
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
                    InventoryAction.objects.create(variety=var_obj, date=seed_date, action_type='SEED',
                                                   quantity=quantity)
            except KeyError:
                pass  # In case there's a variety inconsistency

        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)


@staff_member_required
def inventory_kill(request):
    if request.method == 'GET':
        day = date.today()
        return render(request, 'inventory/inventory_kill.html',
                      context={'variety_list': Variety.objects.all().order_by('name'),
                               'reason_list': KillReason.objects.all(), 'day': day.isoformat()})

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
                    return render(request, 'inventory/inventory_kill.html',
                                  context={'variety_list': Variety.objects.all().order_by('name'),
                                           'reason_list': KillReason.objects.all(),
                                           'day': day, 'date_seeded': date_seeded,
                                           'quantity': quantity,
                                           'selected_variety': variety,
                                           'selected_reasons': reasons,
                                           'error': message})
            else:
                message = "Please enter a positive, non-zero quantity. Check your "
                return render(request, 'inventory/inventory_kill.html',
                              context={'variety_list': Variety.objects.all().order_by('name'),
                                       'reason_list': KillReason.objects.all(),
                                       'day': day, 'date_seeded': date_seeded,
                                       'quantity': quantity,
                                       'selected_variety': variety,
                                       'selected_reasons': reasons,
                                       'error': message})
        except KeyError as e:
            print(e)
            pass  # In case there's a variety inconsistency

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
        return render(request, 'inventory/inventory_recurring.html',
                      context={'day': plant_day, 'weekdays': DAYS_OF_WEEK, 'variety_list': variety_list})

    if request.method == 'POST':
        print(str(request.POST))
        variety_list = []
        for v in Variety.objects.all():
            try:
                day = int(request.POST['day'])
                quantity = int(request.POST['form-plan-' + v.name.replace(" ", "-").replace(":", "").replace(",",
                                                                                                             "") + '-quantity'])
                plan = WeekdayRequirement.objects.get(variety=v, plant_day=day)
                plan.quantity = quantity
                plan.save()
                variety_name_no_spaces = v.name.replace(" ", "-").replace(":", "").replace(",", "")
                variety_list.append((v, variety_name_no_spaces))
            except KeyError:
                pass  # In case there's a variety inconsistency
        # Redirect the user to the weekly planning page
        return render(request, 'inventory/inventory_recurring.html',
                      context={'day': day, 'weekdays': DAYS_OF_WEEK, 'variety_list': variety_list})


@staff_member_required
def inventory_harvest_bulk(request):  # numbers of trays for multiple varieties
    today = date.today().isoformat()
    if request.method == 'GET':
        variety_list = []
        for v in Variety.objects.all().order_by('name'):
            variety_list.append({'name': v.name, 'quantity': None, 'date': None})
        return render(request, 'inventory/inventory_harvest_bulk.html',
                      context={'variety_list': variety_list, 'date': today})

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
                            InventoryAction.objects.create(variety=v, date=h_date, action_type='HARVEST',
                                                           quantity=quantity)
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
                pass  # In case there's a variety inconsistency

        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)


@staff_member_required
def inventory_harvest_variety(request):  # Numbers of trays and yield for a single variety
    today = date.today().isoformat()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_harvest_variety.html',
                      context={'variety_list': Variety.objects.all().order_by('name'), 'date': today})

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
                            InventoryAction.objects.create(variety=var_obj, action_type='HARVEST', quantity=quantity,
                                                           date=h_date)
                    else:
                        message = "There are only " + str(in_house.quantity) + " " + variety + "s for " + seed_date \
                                  + " in your database and you were trying to harvest " + str(
                            quantity) + ". Check your "
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
                              context={'variety_list': Variety.objects.all().order_by('name'), 'date': h_date,
                                       'seed_date': seed_date,
                                       'yield': h_yield, 'quantity': quantity, 'selected_variety': variety,
                                       'error': message})
        except KeyError as e:
            print(e)
            pass  # In case there's a variety inconsistency

        # Redirect the user to the inventory overview page
        return redirect(inventory_overview)


@staff_member_required
def inventory_harvest_single(request):  # One tray, with detailed records
    today = date.today().isoformat()
    if request.method == 'GET':
        return render(request, 'inventory/inventory_harvest_single.html',
                      context={'variety_list': Variety.objects.all().order_by('name'), 'today': today})

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
            print(e)
            pass  # In case there's a variety inconsistency

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
            print(e)
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

    return render(request, "inventory/environment_data.html",
                  context={"rack_channel_no": rack_channel_no, "germ_channel_no": germ_channel_no,
                           "rack_api_key": rack_api_key, "germ_api_key": germ_api_key,
                           "weather_channel_no": weather_channel_no, "weather_api_key": weather_api_key})


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
                slot.barcode = form.cleaned_data.pop('Slot ' + str(slot.id))
                slot.save()
        return redirect(golden_trays_home)
