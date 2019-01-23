from django.test import TestCase
from inventory.models import Slot


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

class CropModelTest(TestCase):
    pass
    

class TrayModelTest(TestCase):
    pass
