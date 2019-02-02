from django.test import TestCase
from inventory.models import Crop, Slot, Variety


class HomePageTest(TestCase):
    """Tests that the homepage works as expected internally."""
    
    def test_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "inventory/index.html")
    
    def test_increase_number_of_trays(self):
        # There are zero total slots before we set slot quantity
        self.assertEqual(0, Slot.objects.count())
        # We hit the set slot qty url
        self.client.post("/slot/set_qty", data={"quantity": 50})
        # Afterwards there is a positive number of total slots
        self.assertEqual(Slot.objects.count(), 50)
        
    def test_decrease_number_of_trays(self):
        # There are five total slots in the database
        slot = [Slot.objects.create() for i in range(5)]
        # We hit the set slot qty url telling it to only have 3 total slots
        response = self.client.post("/slot/set_qty", data={"quantity": 3})
        # And we get an error saying we can't
        self.assertEqual(response.status_code, 400)


class NewCropTest(TestCase):
    """Tests that the new crop page works as expected internally."""

    def test_uses_correct_template(self):
        response = self.client.get("/crop/new/")
        self.assertTemplateUsed(response, "inventory/new_crop.html")

    def test_model_is_updated_correctly(self):
        # Create a single slot
        slot = Slot.objects.create()
        # And two different plant varieties
        Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        Variety.objects.create(name="Radish", days_plant_to_harvest=12)
        # Check that the slot starts out as empty
        self.assertEqual(slot.current_crop, None)
        # Make a post request to the endpoint
        response = self.client.post("/crop/new/", data={"variety": "Radish",
                                                        "tray-size": "1020",
                                                        "delivered-live": "False",
                                                        "germination-length": 4,
                                                        "grow-length": 16,
                                                        "designated-slot-id": 1})
        # Check that the slot now has a crop in it
        slot = Slot.objects.get(id=1)
        self.assertNotEqual(slot.current_crop, None)
        # Check that the crop attributes are all correct
        self.assertEqual(slot.current_crop.variety.name, "Radish")
        self.assertEqual(slot.current_crop.tray_size, "1020")
        self.assertEqual(slot.current_crop.live_delivery, False)
        self.assertEqual(slot.current_crop.exp_num_germ_days, 4)
        self.assertEqual(slot.current_crop.exp_num_grow_days, 16)


class CropModelTest(TestCase):
    pass
    

class TrayModelTest(TestCase):
    pass
