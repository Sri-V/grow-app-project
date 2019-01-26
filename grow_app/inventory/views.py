from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from inventory.models import Crop, Slot, Variety


# Create your views here.
def homepage(request):
    """GET: Display a homepage that offers links to detail pages for crops and slots."""
    total_slot_count = Slot.objects.count()
    return render(request, "inventory/index.html", context={"total_slot_count": total_slot_count})


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
            
    return redirect(homepage)


def create_crop(request):
    """GET: Display a form for new crop data.
    POST: Accept form submission for new crop data, redirect to the new crop's detail page."""
    if request.method == 'GET':
        variety_list = Variety.objects.all()
        slot_list = Slot.objects.all()
        return render(request, "inventory/new_crop.html", context={"variety_list": variety_list, "slot_list": slot_list})

    if request.method == 'POST':
        # TODO -- add input verification check
        variety_name = request.POST["variety"]
        tray_size = str(request.POST["tray-size"])
        delivered_live = bool(request.POST["delivered-live"])
        germination_length = int(request.POST["germination-length"])
        grow_length = int(request.POST["grow-length"])
        designated_slot = int(request.POST["designated-slot"])
        variety = Variety.objects.get(name=variety_name)
        # Create the crop object
        new_crop = Crop.objects.create(variety=variety, tray_size=tray_size, live_delivery=delivered_live, exp_num_germ_days=germination_length, exp_num_grow_days=grow_length)
        # Update the corresponding slot with that crop
        Slot.objects.filter(id=designated_slot).update(current_crop=new_crop)

        return HttpResponseRedirect('/slot/' + str(designated_slot) + '/')


def crop_detail():
    """GET: Display the crop's history, link to its tray."""
    return None


def record_crop_info():
    """POST: Record a timestampped event into the history of this crop's life."""
    return None


def update_crop_lifecycle():
    """POST: Advance the crop from one lifecycle moment to another."""
    return None


def slot_detail(request, slot_id):
    """GET: Displays the details of current crop in the slot and all the buttons used to control a tray in the greenhouse.
    Provides buttons and forms to perform tray actions.This is the page that people using the barcode scanner are going to
     see as they're working all day, so it needs to feel like a control panel."""
    current_crop = Slot.objects.get(id=slot_id).current_crop
    return render(request, "inventory/slot_details.html", context={"current_crop": current_crop})


def slot_action():
    """GET: Display a form for a user to record an action on a tray.
    POST: Update the state of the Tray and make a CropRecord of whatever was done."""
    return None
