"""
This file contains functional tests, meant to test the behavior of the system from the outside.
"""

from django.test import LiveServerTestCase
from selenium import webdriver
from time import sleep

from inventory.models import Slot, Variety

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
        select_delivered_live.find_element_by_css_selector("input[value='false']").click()
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
        self.browser.find_element_by_id("form-new-crop-submit")
        
        # He notices that he's been redirected to the slot detail page
        self.assertEquals(self.browser.current_url, "/slot/2/")
        self.fail("Test incomplete!")
        # Appropriate crop is listed below
        # Navigate to crop detail
        # Crop stuff listed there too
        
    def test_move_crop_from_one_slot_to_another(self):
        # Oliver wants to move his crop from one spot in the greenhouse to another
        self.browser.get(self.live_server_url)
        # He navigates to the slot detail page
        # Then he sees a form that says "Move tray"
        # He clicks the select and chooses another open tray
        # Then he hits submit
        # And he gets redirected to the page belonging to the new slot
        # And the crop is listed below
        # He then goes back to the old slot's page
        # And sees that slot is listed as empty
        self.fail("Test incomplete")
        
    # def test_water_the_crop(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver wants to water a crop of microgreens.
    #
    # def test_harvest_the_crop(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver would like to harvest a crop of microgreens.
    #
    # def test_record_dead_crop(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver notices mold on a crop, and decides to dispose of it.
    #
    # def test_add_note_about_crop(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver wants to record that this crop had its grow lamp die when the bulb burnt out.
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
