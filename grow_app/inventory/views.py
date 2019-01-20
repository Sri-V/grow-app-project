from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from inventory.models import Tray


# Create your views here.
def homepage(request):
    """GET: Display a homepage that offers links to detail pages for crops and trays."""
    tray_count = Tray.objects.count()
    return render(request, "inventory/index.html", context={"tray_count": tray_count})


def set_tray_quantity(request):
    """POST: Update the number of Tray objects, redirect to homepage."""
    desired_tray_count = int(request.POST["quantity"])
    current_tray_count = Tray.objects.count()
    
    if desired_tray_count >= current_tray_count:
        for tray in range(desired_tray_count - Tray.objects.count()):
            Tray.objects.create()
    else:
        # Reducing the number of trays is currently not a supported operation.
        return HttpResponseBadRequest()
            
    return redirect("inventory/index.html")


def create_crop():
    """GET: Display a form for new crop data.
    POST: Accept form submission for new crop data, redirect to the new crop's detail page."""
    return None


def crop_detail():
    """GET: Display the crop's history, link to its tray."""
    return None


def record_crop_info():
    """POST: Record a timestampped event into the history of this crop's life."""
    return None


def update_crop_lifecycle():
    """POST: Advance the crop from one lifecycle moment to another."""
    return None


def tray_detail():
    """GET: Display all the buttons used to control a tray in the greenhouse. Provides buttons and forms to perform
    tray actions.This is the page that people using the barcode scanner are going to see as they're working all day, so
    it needs to feel like a control panel."""
    return None


def tray_action():
    """GET: Display a form for a user to record an action on a tray.
    POST: Update the state of the Tray and make a CropRecord of whatever was done."""
    return None
