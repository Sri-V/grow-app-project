import gspread
from oauth2client.service_account import ServiceAccountCredentials
from inventory.models import Crop, CropAttribute, CropAttributeOption, CropRecord, Slot, Variety


def upload_data_to_drive(crop):
    # Set up to be able to access google sheet
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

    client = gspread.authorize(creds)

    sheet = client.open("TestMicrogreensData").sheet1 # open sheet


    # Date Planted, Crop Variety, Days in Germ (or date out of germ), Days in Grow (date in grow),
    # ... light type, light distance, substrate type, density?, yield, leaf wingspan, notes

    row = []

    # First append the data directly connected to the crop
    row.append(crop.variety.name)
    row.append(crop.germ_days)
    row.append(crop.grow_days)
    row.append(crop.crop_yield)
    row.append(crop.leaf_wingspan)

    # Then iterate through all the attributes
    crop_attributes = crop.attributes.all()
    for attribute in crop_attributes:
        row.append(attribute.name)

    # Finally add the row of data to the sheet
    sheet.append_row(row)








