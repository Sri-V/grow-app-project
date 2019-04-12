"""
This file contains functional tests, meant to test the behavior of the system from the outside.
"""

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from django.utils import dateformat
from selenium import webdriver
from time import sleep
import datetime

from inventory.models import Crop, Slot, Variety, CropRecord
from django.contrib.auth.models import User

SLEEPY_TIME = 1


def simulate_barcode_scan(driver, barcode_text):
    """
    Simulates a barcode scan by executing JavaScript through Selenium that emits our custom barcode-scan event.
    :param driver: a Selenuim WebDriver
    :param barcode_text: String
    :return: None, modifies state of FT.
    """
    barcode_event_script = "let barcodeEvent = new CustomEvent('barcode-scanned', { detail: arguments[0] });" \
                           "document.dispatchEvent(barcodeEvent);"
    driver.execute_script(barcode_event_script, barcode_text)
    sleep(SLEEPY_TIME)


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


class BasicUserInteractionsTest(StaticLiveServerTestCase):
    """
    Tests that the application can support basic crop management tasks post-setup.
    """

    def setUp(self):
        # Set the browser
        self.browser = webdriver.Firefox()

        # Make some slots and save their ids -- this is to avoid hard-coding primary keys in the test methods
        self.plant_origin_slot = Slot.objects.create(barcode="TEST00001")
        self.plant_destination_slot = Slot.objects.create(barcode="TEST00002")
        self.free_slot = Slot.objects.create(barcode="TEST00003")

        # Add some plant varieties
        Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        Variety.objects.create(name="Parsley", days_plant_to_harvest=15)
        Variety.objects.create(name="Radish", days_plant_to_harvest=12)

        # Add a single crop into the first slot
        variety = Variety.objects.get(name="Radish")
        self.first_crop = Crop.objects.create(variety=variety, tray_size="1020", live_delivery=True,
                                              exp_num_germ_days=3, exp_num_grow_days=8)
        Slot.objects.filter(id=self.plant_origin_slot.id).update(current_crop=self.first_crop)
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
        # He hits the button to scan a barcode, and then scans the barcode of the slot he wants
        self.browser.find_element_by_id("form-new-crop-barcode-btn").click()
        simulate_barcode_scan(self.browser, self.free_slot.barcode)
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
        self.assertEqual(self.browser.title, "Crop Details – BMG")
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
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
        # And is redirected to the slot details page
        self.assertEqual("Slot Details – BMG", self.browser.title)
        slot_id = self.browser.find_element_by_id("slot-id").text
        self.assertEqual(slot_id, f'Slot #{self.plant_origin_slot.id}')
        current_crop_type = self.browser.find_element_by_id("current-crop-type").text
        self.assertEqual(current_crop_type, "Current Crop: Radish")
        # He hits the button to scan a barcode
        self.browser.find_element_by_id("form-move-tray-barcode-btn").click()
        # And scans the barcode of the crop's destination slot
        simulate_barcode_scan(self.browser, self.plant_destination_slot.barcode)
        # Then he hits submit and waits
        self.browser.find_element_by_id("form-move-tray-submit").click()

        # And he gets redirected to the page belonging to the new slot
        self.assertRegex(self.browser.current_url, f'/slot/{self.plant_destination_slot.id}/')
        self.assertEqual(self.browser.title, "Slot Details – BMG")
        slot_id = self.browser.find_element_by_id("slot-id").text
        self.assertEqual(slot_id, f'Slot #{self.plant_destination_slot.id}')
        # And the crop is listed below
        current_crop_type = self.browser.find_element_by_id("current-crop-type").text
        self.assertEqual(current_crop_type, "Current Crop: Radish")
        # He then goes back to the old slot's page
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
        # And sees that slot is listed as empty
        self.browser.find_element_by_id("empty-slot")

    def test_water_the_crop(self):
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
        water_crop_form = self.browser.find_element_by_id("form-water-crop")
        # Oliver wants to water a crop of microgreens.
        water_crop_form.find_element_by_css_selector('input[type="submit"]').click()
        # Oliver is redirected to the slot detail page of the watered crop
        self.assertEquals(self.browser.title, "Slot Details – BMG")
        # Verify that a water action was recorded for this crop
        record = CropRecord.objects.filter(record_type='WATER')[0]
        # And the date and time are correct
        self.assertEqual(record.date.today().replace(microsecond=0), datetime.datetime.today().replace(microsecond=0))

    def test_harvest_the_crop(self):
        # Oliver would like to harvest a crop of microgreens.
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
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
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
        # And sees that it is empty
        empty_slot = self.browser.find_element_by_id("empty-slot").text
        self.assertEqual(empty_slot, "Would you like to place a new crop here?")

    def test_record_dead_crop(self):
        # Oliver notices mold on a crop, and decides to dispose of it.
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
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
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
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
        self.assertEqual('Crop Details – BMG', self.browser.title)
        # He reviews the notes about the crop, and sees that the crop lamp bulb has died
        notes = self.browser.find_element_by_id("records").text
        self.assertIn("The crop lamp bulb died", notes)

    def test_lookup_crop_history(self):
        # Oliver wants to look back at the crop's life to understand how it grew.
        # We start by planting a new crop in the empty slot
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}/')
        water_crop_form = self.browser.find_element_by_id("form-water-crop")
        water_crop_form.find_element_by_css_selector('input[type="submit"]').click()
        water_crop_datetime = datetime.datetime.now()
        # And add some records that will show up in the crop history
        self.browser.get(self.live_server_url + f'/slot/{self.plant_origin_slot.id}')
        harvest_crop_form = self.browser.find_element_by_id("form-harvest-crop")
        harvest_crop_form.find_element_by_css_selector('input[type="submit"]').click()
        harvest_crop_datetime = datetime.datetime.now()
        # After harvesting the crop Oliver gets redirected to the crop details page to check the crop history
        self.assertEqual('Crop Details – BMG', self.browser.title)
        # Check that current details of the crop are correct
        crop = Slot.objects.get(id=self.plant_origin_slot.id).current_crop
        seed_date = self.browser.find_element_by_id("seed-date").text
        self.assertEqual(seed_date, "Seeded: " + dateformat.format(self.first_crop_record.date.today(), 'm/d/Y P'))
        last_watered_date = self.browser.find_element_by_id("water-date").text
        self.assertEqual(last_watered_date, "Last watered: " + dateformat.format(water_crop_datetime.today(), 'm/d/Y P'))
        harvested_date = self.browser.find_element_by_id("harvest-date").text
        self.assertEqual(harvested_date, "Harvested: " + dateformat.format(harvest_crop_datetime.today(), 'm/d/Y P'))
        # Check that the newest crop record shows up first and the oldest is last
        records = self.browser.find_element_by_id("records").text

    def test_scan_from_homepage(self):
        # Oliver wants to make sure the that barcode scanning is working correctly
        # when he makes a scan from the homepage
        self.browser.get(self.live_server_url)
        # The barcode of the origin slot is scanned
        simulate_barcode_scan(self.browser, self.plant_origin_slot.barcode)
        # And he sees that he has be redirected to the slot details page for that slot
        self.assertRegex(self.browser.current_url, f"/slot/{self.plant_origin_slot.id}/")
        self.assertEqual(self.browser.title, "Slot Details – BMG")

    def test_add_lifecycle_moment(self):
        # Natalie would like to be able to set the current lifecycle stage of a crop with an additional form
        # First she scans the desired slot
        simulate_barcode_scan(self.browser, self.plant_origin_slot.barcode)
        # Next she then navigates to the crop details page
        self.browser.find_element_by_id("link-crop-details").click()
        # Under the add a record section she selects the growth milestone from the drop down
        select_variety = self.browser.find_element_by_id("form-new-crop-record-type")
        for option in select_variety.find_elements_by_tag_name("option"):
            if option.text == "Growth Milestone":
                option.click()
                break
        else:
            self.fail("The 'Growth Milestone' option was not found in the new crop record form!")
        # Next she adds the date for the growth milestone
        self.browser.find_element_by_id("form-add-crop-record-date").send_keys("3/24/2019, 12:34 PM")
        # Finally she adds a quick note about the record
        self.browser.find_element_by_id("form-add-crop-record-note").send_keys("This one's looking nice!")
        # And hits submit
        self.browser.find_element_by_id("form-add-crop-record-submit").click()
        # When the page refreshes she can see that her crop record has been successfully recorded
        records_list = self.browser.find_element_by_id("records").text
        self.assertIn("03/24/2019 12:34 p.m.", records_list)
        self.assertIn("Growth Milestone", records_list)
        self.assertIn("This one's looking nice!", records_list)


    def test_add_sanitation_record(self):
        # Natalie would like to create a sanitation record after she has sanitized some equipment
        # She first clicks the link in the navbar to get to the sanitation records page
        self.browser.find_element_by_id("link-to-sanitation-records").click()
        # She is then redirected to the sanitation records page
        # And begins to fill out the form
        self.browser.find_element_by_id("id_date").clear()
        self.browser.find_element_by_id("id_date").send_keys("2019-04-10, 9:22:00")
        self.browser.find_element_by_id("id_employee_name").send_keys("Natalie Wannamaker")
        self.browser.find_element_by_id("id_equipment_sanitized").send_keys("Sink")
        self.browser.find_element_by_id("id_chemicals_used").send_keys("Bleach")
        self.browser.find_element_by_id("id_note").send_keys("Not too dirty")
        # After filling out the form she hit the submit button
        self.browser.find_element_by_id("sanitation-form-submit").click()
        # When the page refreshes she can see that the sanitation record has been successfully recorded
        sanitation_records = self.browser.find_element_by_id("records").text
        self.assertIn("4/10/2019 9:22 a.m.", sanitation_records)
        self.assertIn("Natalie Wannamaker", sanitation_records)
        self.assertIn("Sink", sanitation_records)
        self.assertIn("Bleach", sanitation_records)
        self.assertIn("Not too dirty", sanitation_records)







class StaticURLTest(StaticLiveServerTestCase):
    """Tests that the stylesheets and image assets are available from their proper links."""

    def test_base_css_returns_200(self):
        result = finders.find('base.css')
        self.assertIsNotNone(result)

    def test_favicon_returns_200(self):
        result = finders.find('favicon.ico')
        self.assertIsNotNone(result)
