from django.test import TestCase
from inventory.models import Crop, Slot, Variety, CropRecord


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


class MoveTrayTest(TestCase):
    """Tests that move tray action modifies the model correctly."""

    def test_move_crop(self):
        # There are five total slots in the database
        slot = [Slot.objects.create() for i in range(5)]
        # A single crop exists
        variety_basil = Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        basil = Crop.objects.create(variety=variety_basil, tray_size="0505", live_delivery=True, exp_num_germ_days=8, exp_num_grow_days=12)
        # The crop is added to the first slot
        Slot.objects.filter(id=2).update(current_crop=basil)
        # Check that the crop exists in slot 2
        slot = Slot.objects.get(id=2)
        self.assertEqual(slot.current_crop.variety.name, "Basil")
        # And that slot 4 is empty
        slot = Slot.objects.get(id=4)
        self.assertEqual(slot.current_crop, None)
        # Make a post to the move tray endpoint
        response = self.client.post("/slot/2/action/move_tray", data={"slot-destination-id": 4})
        # Check that the crop now lives in slot 4
        slot = Slot.objects.get(id=4)
        self.assertEqual(slot.current_crop.variety.name, "Basil")
        # And that slot 2 is now empty
        slot = Slot.objects.get(id=2)
        self.assertEqual(slot.current_crop, None)


class CropModelTest(TestCase):
    """Unit tests for Crop data structure."""
    pass
    

class SlotModelTest(TestCase):
    """Unit tests for Slot data structure."""
    pass

class AddNoteTest(TestCase):

    def setUp(self):
        self.slot_ids = [Slot.objects.create().id for i in range(3)]
        self.id_of_plant_slot = self.slot_ids[0]
        self.variety_basil = Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        self.basil = Crop.objects.create(variety=self.variety_basil, tray_size="0505", live_delivery=True, exp_num_germ_days=8,
                                    exp_num_grow_days=12)
        # The crop is added to the slot
        Slot.objects.filter(id=self.id_of_plant_slot).update(current_crop=self.basil)

    def testMakeNote(self):
        # Make a note about how the basil lamp died
        note = self.client.post(f'/slot/{self.id_of_plant_slot}/action/note',
                                data={"note": "Basil lamp died"})
        # Check that note is stored in crop record
        record_list = CropRecord.objects.filter(crop=self.basil)
        self.assertEqual(1, len(record_list))
        self.assertEqual("Basil lamp died", record_list[0].note)