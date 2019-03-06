"""
This file contains functional tests, meant to test the behavior of the system from the outside.
"""

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from django.utils import dateformat
from selenium import webdriver
import datetime

from inventory.models import Crop, Slot, Variety, CropRecord
from django.contrib.auth.models import User

SLEEPY_TIME = 1


class GreenhouseSetupTest(LiveServerTestCase):
    """
    Tests that the application can support first-time setup tasks for a greenhouse or growing operation.
    """

    def setUp(self):
        # Set the browser
        self.browser = webdriver.Firefox()

        # Create and login a user
        user = User.objects.create_user(username='test_user', password='password')
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('username').send_keys(user.username)
        self.browser.find_element_by_name('password').send_keys('password')
        self.browser.find_element_by_id('form-login-submit').click()

    def tearDown(self):
        self.browser.quit()

    def test_set_number_of_slots(self):
        # Oliver just learned about this cool new growing app.
        self.browser.get(self.live_server_url + '/growhouse_settings/')
        # He goes to the homepage and reads the title.
        self.assertEqual('Greenhouse Config – BMG', self.browser.title)
        # He sees that he currently has no trays set up.
        body = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Current capacity: 0 slots.", body)
        # He sees that he can put in the number of total slots he has.
        slot_qty = self.browser.find_element_by_id("form-set-slot-count-qty")
        # He types in that he has 400 total slots and hits submit
        slot_qty.send_keys("400")
        self.browser.find_element_by_id("form-set-slot-count-submit").click()

        # He sees that he is redirected to the home page
        self.assertRegex(self.browser.current_url, r"/")
        # He also sees that the number of total slots has updated to 400
        body = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Current capacity: 400 slots.", body)

    def test_add_varieties(self):
        # Oliver wants to input some different crop varieties
        self.browser.get(self.live_server_url + '/growhouse_settings/')
        # He starts by clicking the variety name text box
        add_variety_name = self.browser.find_element_by_id("form-add-variety-name")
        # And adds Kale
        add_variety_name.send_keys("Kale")
        # And sets the expected days until harvest to 18
        add_days_to_harvest = self.browser.find_element_by_id("form-add-variety-days-to-harvest")
        add_days_to_harvest.send_keys(18)
        self.browser.find_element_by_id("form-add-variety-submit").click()
        # He then goes to add Cilantro as another crop
        add_variety_name = self.browser.find_element_by_id("form-add-variety-name")
        add_variety_name.send_keys("Cilantro")
        add_days_to_harvest = self.browser.find_element_by_id("form-add-variety-days-to-harvest")
        add_days_to_harvest.send_keys(10)
        self.browser.find_element_by_id("form-add-variety-submit").click()
        # To check if the varieties have been added he navigates to the add crop page
        self.browser.find_element_by_id("link-to-home").click()
        self.browser.find_element_by_id("link-new-crop").click()
        # He is now on the new crop page
        self.assertEqual(self.browser.title, "New Crop – BMG")
        # After looking at the form options he sees that both varieties are now there
        varieties = []
        variety_selection = self.browser.find_element_by_id("form-new-crop-variety")
        for option in variety_selection.find_elements_by_tag_name("option"):
            varieties.append(option.text)
        self.assertTrue("Kale" in varieties)
        self.assertTrue("Cilantro" in varieties)


class BasicUserInteractionsTest(LiveServerTestCase):
    """
    Tests that the application can support basic crop management tasks post-setup.
    """

    def setUp(self):
        # Set the browser
        self.browser = webdriver.Firefox()

        # Make some slots and save their ids -- this is to avoid hard-coding primary keys in the test methods
        self.plant_origin_slot_id = Slot.objects.create().id
        self.plant_destination_slot_id = Slot.objects.create().id
        self.free_slot_id = Slot.objects.create().id

        # Add some plant varieties
        Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        Variety.objects.create(name="Parsley", days_plant_to_harvest=15)
        Variety.objects.create(name="Radish", days_plant_to_harvest=12)

        # Add a single crop into the first slot
        variety = Variety.objects.get(name="Radish")
        self.first_crop = Crop.objects.create(variety=variety, tray_size="1020", live_delivery=True,
                                              exp_num_germ_days=3, exp_num_grow_days=8)
        Slot.objects.filter(id=self.plant_origin_slot_id).update(current_crop=self.first_crop)
        # And record the SEED record
        self.first_crop_record = CropRecord.objects.create(crop=self.first_crop, record_type='SEED')

        # Create and login a user
        user = User.objects.create_user(username='test_user', password='password')
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('username').send_keys(user.username)
        self.browser.find_element_by_name('password').send_keys('password')
        self.browser.find_element_by_id('form-login-submit').click()

    def tearDown(self):
        self.browser.quit()

    def test_plant_new_crop_in_a_slot(self):
        # Oliver wants to plant a new crop to track with the growing app.
        self.browser.get(self.live_server_url)
        # He clicks a link to add a new crop
        self.browser.find_element_by_id("link-new-crop").click()
        # He lands on a page that presents a form for adding a new crop
        self.assertRegex(self.browser.current_url, r"/crop/new/")
        self.assertEqual(self.browser.title, "New Crop – BMG")
        # He selects Basil from the variety dropdown menu
        select_variety = self.browser.find_element_by_id("form-new-crop-variety")
        for option in select_variety.find_elements_by_tag_name("option"):
            if option.text == "Basil":
                option.click()
                break
        else:
            self.fail("The 'Basil' option was not found in the new crop form!")
        # He selects a 10" by 10" tray
        self.browser.find_element_by_id("form-new-crop-tray-size-1010").click()
        # He opts to have the tray harvested on-site
        self.browser.find_element_by_id("form-new-crop-delivered-live-false").click()
        # He enters that the crop should germinate for 5 days and grow for another 10
        self.browser.find_element_by_id("form-new-crop-germination-length").send_keys("5")
        self.browser.find_element_by_id("form-new-crop-grow-length").send_keys("10")
        # FIXME -- he scans the barcode of the slot in which the crop will live
        select_slot = self.browser.find_element_by_id("form-new-crop-slot")
        for option in select_slot.find_elements_by_tag_name("option"):
            if option.text == str(self.free_slot_id):
                option.click()
                break
        else:
            self.fail(f'Unable to find Tray #{self.free_slot_id} in the new crop form!')
        # Then he hits submit and waits
        self.browser.find_element_by_id("form-new-crop-submit").click()

        # He notices that he's been redirected to the slot detail page
        self.assertRegex(self.browser.current_url, r"/slot/\d+/")
        self.assertEqual(self.browser.title, "Slot Details – BMG")
        # And he sees that the appropriate crop is listed below
        current_crop_type = self.browser.find_element_by_id("current-crop-type").text
        self.assertEqual(current_crop_type, "Current Crop: Basil")
        # He navigates to the crop detail/history page
        self.browser.find_element_by_id("link-crop-details").click()
        self.assertEqual(self.browser.title, "Crop Details")
        # And he sees the crop's history and any other info that wasn't included on the slot detail page
        crop_type = self.browser.find_element_by_id("crop-type").text
        self.assertEqual(crop_type, "Crop Type: Basil")
        tray_size = self.browser.find_element_by_id("tray-size").text
        self.assertEqual(tray_size, "Tray Size: 10\" × 10\"")
        live_delivery = self.browser.find_element_by_id("live-delivery").text
        self.assertEqual(live_delivery, "Live Delivery: False")
        exp_num_germ_days = self.browser.find_element_by_id("exp-num-germ-days").text
        self.assertEqual(exp_num_germ_days, "Expected number of germination days: 5")
        exp_num_grow_days = self.browser.find_element_by_id("exp-num-grow-days").text
        self.assertEqual(exp_num_grow_days, "Expected number of grow days: 10")

    def test_move_crop_from_one_slot_to_another(self):
        # Oliver wants to move his crop from one spot in the greenhouse to another
        # FIXME -- He scans the barcode of the radish tray he would like to move
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}/')
        # And is redirected to the slot details page
        self.assertEqual("Slot Details – BMG", self.browser.title)
        slot_id = self.browser.find_element_by_id("slot-id").text
        self.assertEqual(slot_id, f'Slot #{self.plant_origin_slot_id}')
        current_crop_type = self.browser.find_element_by_id("current-crop-type").text
        self.assertEqual(current_crop_type, "Current Crop: Radish")

        # FIXME -- He scans the barcode of the crop's destination slot
        select_slot_destination = self.browser.find_element_by_id("form-move-tray-destination-id")
        for option in select_slot_destination.find_elements_by_tag_name("option"):
            if option.text == str(self.plant_destination_slot_id):
                option.click()
                break
        else:
            self.fail(f'Unable to find destination tray #{self.plant_destination_slot_id} in the dropdown menu!')
        # Then he hits submit and waits
        self.browser.find_element_by_id("form-move-tray-submit").click()

        # And he gets redirected to the page belonging to the new slot
        self.assertRegex(self.browser.current_url, f'/slot/{self.plant_destination_slot_id}/')
        self.assertEqual(self.browser.title, "Slot Details – BMG")
        slot_id = self.browser.find_element_by_id("slot-id").text
        self.assertEqual(slot_id, f'Slot #{self.plant_destination_slot_id}')
        # And the crop is listed below
        current_crop_type = self.browser.find_element_by_id("current-crop-type").text
        self.assertEqual(current_crop_type, "Current Crop: Radish")
        # He then goes back to the old slot's page
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}/')
        # And sees that slot is listed as empty
        self.browser.find_element_by_id("empty-slot")

    def test_water_the_crop(self):
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}')
        water_crop_form = self.browser.find_element_by_id("form-water-crop")
        # Oliver wants to water a crop of microgreens.
        water_crop_form.find_element_by_css_selector('input[type="submit"]').click()
        # Verify that a water action was recorded for this crop
        record = CropRecord.objects.filter(record_type='WATER')[0]
        # And the date and time are correct
        self.assertEqual(record.date.today().replace(microsecond=0), datetime.datetime.today().replace(microsecond=0))

    def test_harvest_the_crop(self):
        # Oliver would like to harvest a crop of microgreens.
        # He navigates to the slot details page of the slot he'd like to harvest
        # FIXME -- he scans the slot of interest with the barcode scanner
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}/')
        # Then he finds the form for harvesting a crop
        harvest_crop_form = self.browser.find_element_by_id("form-harvest-crop")
        # He clicks the submit button to harvest the crop
        harvest_crop_form.find_element_by_css_selector('input[type="submit"]').click()
        # Then he gets redirected to the crop history
        self.assertRegex(self.browser.current_url, f'/crop/{self.first_crop.id}/')
        # And the history displays a crop record indicating it was harvested
        harvest_text = self.browser.find_element_by_id("harvest-date").text
        self.assertEqual("Harvested: " + dateformat.format(datetime.datetime.now(), 'm/d/Y P'), harvest_text)
        # Then he navigates back to the slot that the crop was in
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}/')
        # And sees that it is empty
        empty_slot = self.browser.find_element_by_id("empty-slot").text
        self.assertEqual(empty_slot, "Would you like to place a new crop here?")

    def test_record_dead_crop(self):
        # Oliver notices mold on a crop, and decides to dispose of it.
        # FIXME -- he scans the slot of interest with the barcode scanner
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}/')
        # And is redirected to the slot details page
        self.assertEqual("Slot Details – BMG", self.browser.title)
        current_crop_type = self.browser.find_element_by_id("current-crop-type").text
        self.assertEqual(current_crop_type, "Current Crop: Radish")
        # He writes that mold is the reason for trashing the crop
        self.browser.find_element_by_id("form-record-dead-crop-reason").send_keys("mold on crop")
        # And clicks on the button to record a dead crop
        self.browser.find_element_by_id("form-record-dead-crop-submit").click()
        # The slot details page reloads and he sees that the crop has been removed from the slot
        empty_slot = self.browser.find_element_by_id("empty-slot")
        # Oliver then navigates to the crop details page to look at the crop history
        self.browser.get(self.live_server_url + f'/crop/{self.first_crop.id}/')
        self.assertEqual("Crop Details – BMG", self.browser.title)
        # Under the crop history section he sees that the trashed crop record has been recorded
        trashed_record = self.browser.find_element_by_id("trash-date").text
        self.assertEqual(trashed_record, "Trashed: " + dateformat.format(datetime.datetime.today(), 'm/d/Y P'))

    def test_add_note_about_crop(self):
        # Oliver wants to record that this crop had its grow lamp die when the bulb burnt out.
        # FIXME -- he scans the slot of interest with the barcode scanner
        self.browser.get(self.live_server_url + "/slot/1/")
        # He gets directed be on the page associated with that slot
        self.assertEqual('Slot Details – BMG', self.browser.title)
        # Oliver types a note about the crop in the notes field
        self.browser.find_element_by_name("note").send_keys("The crop lamp bulb died")
        # Oliver hits the submit button
        self.browser.find_element_by_id("form-record-note-submit").click()
        # He is then redirected back to the slot details page
        self.assertEqual('Slot Details – BMG', self.browser.title)
        # He then clicks the crop details link to see the crop details
        self.browser.find_element_by_id("link-crop-details").click()
        # He is directed to the crop details page
        self.assertEqual('Crop Details', self.browser.title)
        # He reviews the notes about the crop, and sees that the crop lamp bulb has died
        notes = self.browser.find_element_by_id("note-text").text
        self.assertEqual("The crop lamp bulb died", notes)

    def test_lookup_crop_history(self):
        # Oliver wants to look back at the crop's life to understand how it grew.
        # We start by planting a new crop in the empty slot
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}')
        water_crop_form = self.browser.find_element_by_id("form-water-crop")
        water_crop_form.find_element_by_css_selector('input[type="submit"]').click()
        water_crop_datetime = datetime.datetime.now()
        # And add some records that will show up in the crop history
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot_id}')
        harvest_crop_form = self.browser.find_element_by_id("form-harvest-crop")
        harvest_crop_form.find_element_by_css_selector('input[type="submit"]').click()
        harvest_crop_datetime = datetime.datetime.now()
        # After harvesting the crop Oliver gets redirected to the crop details page to check the crop history
        self.assertEqual('Crop Details', self.browser.title)
        # Check that current details of the crop are correct
        crop = Slot.objects.get(id=self.plant_origin_slot_id).current_crop
        seed_date = self.browser.find_element_by_id("seed-date").text
        self.assertEqual(seed_date, "Seeded: " + dateformat.format(self.first_crop_record.date.today(), 'm/d/Y P'))
        last_watered_date = self.browser.find_element_by_id("water-date").text
        self.assertEqual(last_watered_date, "Last watered: " + dateformat.format(water_crop_datetime.today(), 'm/d/Y P'))
        harvested_date = self.browser.find_element_by_id("harvest-date").text
        self.assertEqual(harvested_date, "Harvested: " + dateformat.format(harvest_crop_datetime.today(), 'm/d/Y P'))
        # Check that the newest crop record shows up first and the oldest is last
        records = self.browser.find_element_by_id("records").text


class StaticURLTest(StaticLiveServerTestCase):
    """Tests that the stylesheets and image assets are available from their proper links."""

    def test_base_css_returns_200(self):
        result = finders.find('base.css')
        self.assertIsNotNone(result)

    def test_favicon_returns_200(self):
        result = finders.find('favicon.ico')
        self.assertIsNotNone(result)
