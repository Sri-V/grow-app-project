# your imports, e.g. Django models
from inventory.models import *

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grow_app.settings")


def add_barcodes(file):
    with open(file) as f:
        lines = [line.rstrip('\n') for line in f]
    for bc in lines:
        Slot.objects.create(barcode=bc)
