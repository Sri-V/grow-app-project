"""
This file contains functional tests, meant to test the behavior of the system from the outside.
"""

from django.test import LiveServerTestCase
from selenium import webdriver
from time import sleep

SLEEPY_TIME = 1


class BasicInventoryInteractionsTest(LiveServerTestCase):
    def setUp(self):
        # Set the browser
        self.browser = webdriver.Firefox()
        
    def tearDown(self):
        self.browser.quit()
        
    ###
    # SPRINT 1
    ###
        
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
        
    # def test_plant_new_crop_in_a_slot(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver wants to plant a new crop to track with the growing app.
    #     # He goes to the website
    #
    # def test_move_crop_from_one_slot_to_another(self):
    #     self.browser.get(self.live_server_url)
    #     self.fail("Test incomplete")
    #     # Oliver wants to move his crop from one spot in the greenhouse to another
        
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
