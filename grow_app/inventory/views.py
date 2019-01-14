from django.shortcuts import render


# Create your views here.
def homepage():
    """GET: Display a homepage that offers links to detail pages for crops and trays."""
    return None


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
