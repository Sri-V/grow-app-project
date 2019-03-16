from django.test import TestCase
from inventory.models import Crop, Slot, Variety, CropRecord
from django.contrib.auth.models import User
from django.test import Client


def login_the_test_user(test_case):
    test_case.user = User.objects.create_user(username="test", email="test@test.com", password="test")
    test_case.user.save()
    test_case.client.login(username="test", password="test")


class HomePageTest(TestCase):
    """Tests that the homepage works as expected internally."""

    # Logs in the user before the test starts
    def setUp(self):
        self.client = Client()
        login_the_test_user(self)

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

    def setUp(self):
        self.client = Client()
        login_the_test_user(self)

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

    def test_new_crop_form_does_not_replace_original(self):
        # Set up form options
        slot = Slot.objects.create()
        Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        Variety.objects.create(name="Radish", days_plant_to_harvest=12)
        # Make a post request to the new crop endpoint
        response = self.client.post("/crop/new/", data={"variety": "Radish",
                                                        "tray-size": "1020",
                                                        "delivered-live": "False",
                                                        "germination-length": 4,
                                                        "grow-length": 16,
                                                        "designated-slot-id": 1})
        # Check that the slot now has a crop in it
        slot = Slot.objects.get(id=1)
        self.assertNotEqual(slot.current_crop, None)
        self.assertEqual(slot.current_crop.variety.name, "Radish")
        # Make another submission to try to add a new crop in the same slot
        response = self.client.post("/crop/new/", data={"variety": "Basil",
                                                        "tray-size": "1010",
                                                        "delivered-live": "True",
                                                        "germination-length": 8,
                                                        "grow-length": 10,
                                                        "designated-slot-id": 1})
        # Check that we get a 400 error since our post request should not go through
        self.assertEqual(response.status_code, 400)
        # And we see that the original crop remains in the slot
        self.assertEqual(slot.current_crop.variety.name, "Radish")


class MoveTrayTest(TestCase):
    """Tests that move tray action modifies the model correctly."""

    def setUp(self):
        self.client = Client()
        login_the_test_user(self)

    def test_move_crop(self):
        # There are five total slots in the database
        slot = [Slot.objects.create() for i in range(5)]
        # A single crop exists
        variety_basil = Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        basil = Crop.objects.create(variety=variety_basil, tray_size="0505", live_delivery=True, exp_num_germ_days=8, exp_num_grow_days=12)
        # The crop is added to slot 2
        Slot.objects.filter(id=2).update(current_crop=basil)
        # Check that the crop exists in slot 2
        slot = Slot.objects.get(id=2)
        self.assertEqual(slot.current_crop.variety.name, "Basil")
        # And that slot 4 is empty
        slot = Slot.objects.get(id=4)
        self.assertEqual(slot.current_crop, None)
        # Make a post to the move tray endpoint
        response = self.client.post("/slot/2/action/move_tray", data={"slot-destination-id": 4,
                                                                      "slot-destination-phase": "-- none --"})
        # Check that the crop now lives in slot 4
        slot = Slot.objects.get(id=4)
        self.assertEqual(slot.current_crop.variety.name, "Basil")
        # And that slot 2 is now empty
        slot = Slot.objects.get(id=2)
        self.assertEqual(slot.current_crop, None)


class RecordDeadCropTest(TestCase):
    """Tests that the record dead crop action modifies the model correctly."""

    def setUp(self):
        self.client = Client()
        login_the_test_user(self)

    def test_record_dead_crop(self):
        # We create a single slot in the database
        Slot.objects.create()
        # And a crop to go in the slot
        variety_basil = Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        basil = Crop.objects.create(variety=variety_basil, tray_size="0505", live_delivery=True, exp_num_germ_days=8, exp_num_grow_days=12)
        # The crop is added to the slot
        Slot.objects.filter(id=1).update(current_crop=basil)
        # Check that the crop exists in the slot
        slot = Slot.objects.get(id=1)
        self.assertEqual(slot.current_crop.variety.name, "Basil")
        # And check that there is no TRASH record that has been recorded for this crop
        num_trash_records = len(CropRecord.objects.filter(crop=basil).filter(record_type='TRASH'))
        self.assertEqual(num_trash_records, 0)
        # Make a post to the record dead crop endpoint
        response = self.client.post("/slot/1/action/trash", data={"reason-for-trash-text": "Got frozen"})
        # Check that there is no longer a crop in the slot
        current_crop = Slot.objects.get(id=1).current_crop
        self.assertIsNone(current_crop)
        # Check that a single crop record has now been created
        num_trash_records = len(CropRecord.objects.filter(crop=basil).filter(record_type='TRASH'))
        self.assertEqual(num_trash_records, 1)
        # Check that the crop record was created and contains the reason for trashing
        trash_record = CropRecord.objects.filter(crop=basil).filter(record_type='TRASH')[0]
        self.assertEqual(trash_record.crop.variety.name, "Basil")
        self.assertEqual(trash_record.note, "Got frozen")


class AddNoteTest(TestCase):
    """Unit test that we can add a note to a crop and have it appear in the crop history."""
    def setUp(self):
        self.slot_ids = [Slot.objects.create().id for i in range(3)]
        self.id_of_plant_slot = self.slot_ids[0]
        self.variety_basil = Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        self.basil = Crop.objects.create(variety=self.variety_basil, tray_size="0505", live_delivery=True, exp_num_germ_days=8,
                                    exp_num_grow_days=12)
        # The crop is added to the slot
        Slot.objects.filter(id=self.id_of_plant_slot).update(current_crop=self.basil)
        
        self.client = Client()
        login_the_test_user(self)

    def testMakeNote(self):
        # Make a note about how the basil lamp died
        note = self.client.post(f'/slot/{self.id_of_plant_slot}/action/note',
                                data={"note": "Basil lamp died"})
        # Check that note is stored in crop record
        record_list = CropRecord.objects.filter(crop=self.basil)
        self.assertEqual(1, len(record_list))
        self.assertEqual("Basil lamp died", record_list[0].note)


class BarcodeRedirectTest(TestCase):
    """Unit test that we can use the barcode URI to redirect to a slot page."""
    
    def setUp(self):
        self.client = Client()
        self.barcode_text = "G0010101"
        self.slot = Slot.objects.create(barcode=self.barcode_text)
        login_the_test_user(self)
    
    def testBarcodeRedirect(self):
        self.client.get(f'/barcode/{self.barcode_text}/')
        self.fail("Finish the test!")
