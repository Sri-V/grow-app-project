"""
This file contains functional tests, meant to test the behavior of the system from the outside.
"""

from django.test import LiveServerTestCase
from selenium import webdriver
from time import sleep

from inventory.models import Crop, Slot, Variety

SLEEPY_TIME = 1

class GreenhouseSetupTest(LiveServerTestCase):
    """
    Tests that the application can support first-time setup tasks for a greenhouse or growing operation.
    """
    def setUp(self):
        # Set the browser
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_new_user_setup(self):
        # Oliver just learned about this cool new growing app.
        self.browser.get(self.live_server_url)
        # He goes to the homepage and reads the title.
        self.assertEqual('Home -- BMG', self.browser.title)  # TODO -- cooler name
        # He sees that he currently has no trays set up.
        body = self.browser.find_element_by_tag_name("body").text
        self.assertIn("You have 0 total slots.", body)
        # He sees that he can put in the number of total slots he has.
        slot_qty = self.browser.find_element_by_id("form-set-slot-count-qty")
        # He types in that he has 400 total slots and hits submit
        slot_qty.send_keys("400")
        self.browser.find_element_by_id("form-set-slot-count-submit").click()
        sleep(SLEEPY_TIME)

        # He sees that he is redirected to the home page
        self.assertRegex(self.browser.current_url, r"/")
        # He also sees that the number of total slots has updated to 400
        body = self.browser.find_element_by_tag_name("body").text
        self.assertIn("You have 400 total slots.", body)
        # TODO -- Add variety information too


class BasicUserInteractionsTest(LiveServerTestCase):
    """
    Tests that the application can support basic crop management tasks post-setup.
    """

    def setUp(self):
        # Set the browser
        self.browser = webdriver.Firefox()

        # Add slots in the greenhouse
        for i in range(5):
            Slot.objects.create()

        # Add some plant varieties
        Variety.objects.create(name="Basil", days_plant_to_harvest=20)
        Variety.objects.create(name="Parsley", days_plant_to_harvest=15)
        Variety.objects.create(name="Radish", days_plant_to_harvest=12)

        # Add a single crop into the first slot
        variety = Variety.objects.get(name="Radish")
        first_crop = Crop.objects.create(variety=variety, tray_size="1020", live_delivery=True, exp_num_germ_days=3, exp_num_grow_days=8)
        Slot.objects.filter(id=1).update(current_crop=first_crop)

    def tearDown(self):
        self.browser.quit()

    def test_plant_new_crop_in_a_slot(self):
        # Oliver wants to plant a new crop to track with the growing app.
        # He goes to the website and sees that his slots are there
        self.browser.get(self.live_server_url)
        body = self.browser.find_element_by_tag_name("body").text
        self.assertIn("You have 5 total slots.", body)
        # Then he clicks a link to add a new crop
        self.browser.find_element_by_id("link-new-crop").click()
        # He lands on a page that presents a form for adding a new crop
        self.assertRegex(self.browser.current_url, r"/crop/new/")
        self.assertEqual(self.browser.title, "New Crop -- BMG")
        # He selects Basil from the vareity dropdown menu
        select_variety = self.browser.find_element_by_id("form-new-crop-variety")
        for option in select_variety.find_elements_by_tag_name("option"):
            if option.text == "Basil":
                option.click()
                break
        else:
            self.fail("The 'Basil' option was not found in the new crop form!")
        # He selects a 10" by 10" tray
        select_tray_size = self.browser.find_element_by_id("form-new-crop-tray-size")
        select_tray_size.find_element_by_css_selector("input[value='1010']").click()
        # He opts to have the tray harvested on-site
        select_delivered_live = self.browser.find_element_by_id("form-new-crop-delivered-live")
        select_delivered_live.find_element_by_css_selector("input[value='False']").click()
        # He enters that the crop should germinate for 5 days and grow for another 10
        self.browser.find_element_by_id("form-new-crop-germination-length").send_keys("5")
        self.browser.find_element_by_id("form-new-crop-grow-length").send_keys("10")
        # Lastly he selects an open slot from a dropdown list
        # TODO -- this selection should be a barcode scan
        select_slot = self.browser.find_element_by_id("form-new-crop-slot")
        for option in select_slot.find_elements_by_tag_name("option"):
            if option.text == "2":
                option.click()
                break
        else:
            self.fail("Unable to find Tray #2 in the new crop form!")
        # Then he hits submit
        self.browser.find_element_by_id("form-new-crop-submit").click()
        # He notices that he's been redirected to the slot detail page
        self.assertRegex(self.browser.current_url, r"/slot/2/")
        self.assertEqual(self.browser.title, "Slot Details")
        # Appropriate crop is listed below
        current_crop_type = self.browser.find_element_by_id("current-crop-type").text
        self.assertEqual(current_crop_type, "Current Crop: Basil")
        # Navigate to crop detail
        self.browser.find_element_by_id("link-crop-details").click()
        # He finds himself redirected to the crop details page
        self.assertRegex(self.browser.current_url, r"/crop/2/")
        self.assertEqual(self.browser.title, "Crop Details")
        # Crop stuff listed there too
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

        # possibly add list of slot "locations" that the crop is in


    # def test_move_crop_from_one_slot_to_another(self):
    #     # Oliver wants to move his crop from one spot in the greenhouse to another
    #     # He scans the barcode of the slot he would like to move
    #     self.browser.get(self.live_server_url + "/slot/1/")
    #     # And is redirected to the slot details page
    #     self.assertEqual(self.browser.title, "Slot Details")
    #     slot_id = self.browser.find_element_by_id("slot-id").text
    #     self.assertEqual(slot_id, "Slot ID: 1")
    #     # Then he clicks the button that says "Move tray"
    #     self.browser.find_element_by_id("button-move-tray-submit").click
    #     # He is redirected to a form that allows him to enter the new slot number or scan it with a barcode
    #     # He fills out the form manualy and hits submit
    #     self.browser.find_element_by_id("form-move-to-slot").send_keys("4")
    #     self.browser.find_element_by_id("form-move-to-slot-submit").click()
    #     # And he gets redirected to the page belonging to the new slot
    #     self.assertRegex(self.browser.current_url, r"/crop/4/")
    #     self.assertEqual(self.browser.title, "Slot Details")
    #     slot_id = self.browser.find_element_by_id("slot-id").text
    #     self.assertEqual(slot_id, "Slot ID: 1")
    #     # And the crop is listed below
    #     current_crop_type = self.browser.find_element_by_id("current-crop-type").text
    #     self.assertEqual(current_crop_type, "Current Crop: Basil")
    #     # He then goes back to the old slot's page
    #     self.browser.get(self.live_server_url + "/slot/1/")
    #     # And sees that slot is listed as empty
    #     current_crop_type = self.browser.find_element_by_id("current-crop-type").text
    #     self.assertEqual(current_crop_type, "Current Crop: ")
    #
    # def test_water_the_crop(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver wants to water a crop of microgreens.
    #
    # def test_harvest_the_crop(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver would like to harvest a crop of microgreens.

    def test_record_dead_crop(self):
        # Oliver notices mold on a crop, and decides to dispose of it.
        # He scans slot 1 with the barcode scanner
        self.browser.get(self.live_server_url + "/slot/1/")
        # And is redirected to the slot details page
        self.assertEqual(self.browser.title, "Slot Details")
        # He clicks on the button to record a dead crop
        self.browser.find_element_by_id("form-record-dead-crop-submit").click()
        # He is redirected to the home page
        self.assertEqual('Home -- BMG', self.browser.title)


    def test_add_note_about_crop(self):

        bulb_died = "The crop lamp bulb died";

        # Oliver wants to record that this crop had its grow lamp die when the bulb burnt out.
        # He scans slot 1 with the barcode scanner
        self.browser.get(self.live_server_url + "/slot/1/")
        # He gets directed be on the page associated with that slot
        self.assertEqual(self.browser.title, "Slot Details")
        # Oliver types a note about the crop in the notes field
        self.browser.find_element_by_name("note").send_keys(bulb_died)
        # Oliver hits the submit button
        self.browser.find_element_by_id("form-record-note-submit").click()
        # He is then redirected back to the home page
        self.assertEqual('Home -- BMG', self.browser.title)

    # def test_add_note_about_crop(self):
    #     # Oliver wants to record that this crop had its grow lamp die when the bulb burnt out.
    #     # He scans slot 1 with the barcode scanner
    #     self.browser.get(self.live_server_url + "/slot/1/")
    #     # He gets directed be on the page associated with that slot
    #     self.assertEqual(self.browser.title, "Slot Details")
    #     # Oliver clicks a button to add a note to the crop
    #     # He gets redirected to the notes page
    #     # He writes a note about what happened and hits submit
    #     # He is then redirected back to the slot details page
    #     self.fail("Test incomplete")
    #
    #
    # def test_lookup_crop_history(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver wants to look back at the crop's life to understand how it grew.
    #
    # ###
    # # SPRINT 2
    # ###
    #
    # def test_interact_with_groups_of_slots(self):
    #     self.fail("Test incomplete")
    #     # Oliver wants to make a group of addresses that represents a rack
    #
    # def test_interact_with_groups_of_crops(self):
    #     self.fail("Test incomplete")
    #     # Oliver wants to label 10 specific crops as experimental (comparing brands of fertilizer).
    #
    # def test_bulk_plant_water(self):
    #     self.fail("Test incomplete")
    #     # Oliver wants to water an entire rack of trays all at once.
    #
    # def test_bulk_plant_harvest(self):
    #     self.fail("Test incomplete")
    #     # Oliver wants to harvest an entire rack of trays all at once.
