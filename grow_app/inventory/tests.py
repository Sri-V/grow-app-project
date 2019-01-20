from django.test import TestCase
from inventory.models import Tray


class HomePageTest(TestCase):
    """Tests that the homepage works as expected internally."""
    
    def test_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "inventory/index.html")
    
    def test_increase_number_of_trays(self):
        # There are zero trays before we set tray quantity
        self.assertEqual(0, Tray.objects.count())
        # We hit the set tray qty url
        self.client.post("/tray/set_qty", data={"quantity": 50})
        # Afterwards there are trays
        self.assertEqual(Tray.objects.count(), 50)
        
    def test_decrease_number_of_trays(self):
        # There are five trays in the database
        trays = [Tray.objects.create() for i in range(5)]
        # We hit the set tray qty url telling it to only have 3 trays
        response = self.client.post("/tray/set_qty", data={"quantity": 3})
        # And we get an error saying we can't
        self.assertEqual(response.status_code, 400)
        

class CropModelTest(TestCase):
    pass
    

class TrayModelTest(TestCase):
    pass
