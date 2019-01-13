"""
This file contains functional tests, meant to test the behavior of the system from the outside.
"""

from django.test import LiveServerTestCase
from selenium import webdriver


class BasicInventoryInteractionsTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        
    def tearDown(self):
        self.browser.quit()
        
    ###
    # SPRINT 1
    ###
        
    def test_new_user_setup(self):
        self.fail("Test incomplete")
        # Oliver just learned about this cool new growing app.
        # He goes to the homepage and sees that he can specify the capacity of his greenhouse.
        
    def test_plant_new_crop_in_a_tray(self):
        self.fail("Test incomplete")
        # Oliver wants to plant a new crop to track with the growing app.
        # He goes to the website
        
    def test_water_the_crop(self):
        self.fail("Test incomplete")
        # Oliver wants to water a crop of microgreens.
        
    def test_harvest_the_crop(self):
        self.fail("Test incomplete")
        # Oliver would like to harvest a crop of microgreens.
        
    def test_record_dead_crop(self):
        self.fail("Test incomplete")
        # Oliver notices mold on a crop, and decides to dispose of it.
        
    def test_add_note_about_crop(self):
        self.fail("Test incomplete")
        # Oliver wants to record that this crop had its grow lamp die when the bulb burnt out.
        
    def test_lookup_crop_history(self):
        self.fail("Test incomplete")
        # Oliver wants to look back at the crop's life to understand how it grew.
    
    ###
    # SPRINT 2
    ###
    
    def test_interact_with_groups_of_trays(self):
        self.fail("Test incomplete")
        # Oliver wants to group his trays together on a rack.
        # Oliver wants to label 10 specific plants as experimental (comparing brands of fertilizer).
    
    def test_bulk_plant_water(self):
        self.fail("Test incomplete")
        # Oliver wants to water an entire rack of trays all at once.
        
    def test_bulk_plant_harvest(self):
        self.fail("Test incomplete")
        # Oliver wants to harvest an entire rack of trays all at once.
