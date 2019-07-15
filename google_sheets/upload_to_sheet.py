import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def upload_data_to_sheets(crop):
    # Set up to be able to access google sheet
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    env_private_key = os.environ.get('SHEETS_API_KEY').replace('\\n', '\n')
    credentails = {
        "type": "service_account",
        "project_id": "microgreens-245221",
        "private_key_id": "cd23019fa78b82360026bc27731439520cba19d1",
        "private_key": env_private_key,
        "client_email": "stenzel@microgreens-245221.iam.gserviceaccount.com",
        "client_id": "110324471923721786838",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/stenzel%40microgreens-245221.iam.gserviceaccount.com"
    }

    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentails, scope)

    client = gspread.authorize(creds)

    sheet = client.open("TestMicrogreensData").sheet1  # open sheet

    # Date Planted, Crop Variety, Days in Germ (or date out of germ), Days in Grow (date in grow),
    # ... light type, light distance, substrate type, density?, yield, leaf wingspan, notes

    row = []

    # First append the data directly connected to the crop
    # crop_link = "https://bostonmicrogreens.herokuapp.com/crop/%d/" % crop.id
    crop_link = "http://127.0.0.1:8001/crop/%d/" % crop.id
    full_hyperlink = '=HYPERLINK("' + crop_link + '", "' + crop.variety.name + '")'

    row.append(crop.variety.name)  # Variety
    row.append(crop.grow_date.strftime("%m/%d/%y"))  # Date Planted
    row.append(crop.days_in_germ())  # Germ Days
    row.append(crop.days_in_grow())  # Grow Days
    row.append(crop.crop_yield)  # Crop Yield
    row.append(crop.leaf_wingspan)  # Leaf Wingspan
    row.append(crop.notes)  # Notes

    # Add a link to the crop
    row.append(crop_link)  # Crop URL

    # Add the list of all the dates that the crop was watered
    water_records = crop.croprecord_set.filter(record_type='WATER')
    water_dates = ','.join([record.date.strftime("%m/%d/%y") for record in water_records])
    row.append(water_dates)  # Dates Watered

    # Then iterate through all the attributes
    crop_attributes = crop.attributes.all()
    for attribute in crop_attributes:
        row.append(attribute.name)

    # Finally add the row of data to the sheet
    sheet.append_row(row)








