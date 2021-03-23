"""
    excel_scrape
    Scrapes excel any new patient sheets manually placed into worker/patients directory, 
    Matches patients w potential reviews

"""
from typing_extensions import Annotated
import os
import openpyxl
import json
import requests


def getPatients():
    potential_matches = []
    no_matches = []

    patient_names = set()

    # open excels_documented
    f = open('excels_documented.txt', 'r+')
    already_scraped = set(line.rstrip('\n') for line in f)
    scraped = set()

    f1 = open('google_reviews.txt')
    data = json.load(f1)

    for filename in os.listdir('./patients'):
        if filename.endswith('.xlsx') and filename not in already_scraped:
                wb = openpyxl.load_workbook(os.path.join('./patients', filename))
                sheet = wb['Sheet1']
                end = sheet.max_row
                N, first, last, phone, email = 6, 0, 1, 2, 4
                for i in range (2, end + 1):
                    if str(sheet[i][N-1].value).lower() == 'yes':
                        first_name, last_name, email_address, phone_number = getPatientInfo(i, sheet, first, last, email, phone)
                        # generate patient object
                        if last_name is not None:
                            patient_name = first_name + ' ' + last_name
                        else:
                            patient_name = first_name
                        if patient_name not in patient_names:
                            patient_names.add(patient_name)
                            patient = generatePatientObj(patient_name, filename, phone_number, email_address)

                            # generate names and variations set
                            name_variations = generateNames(first_name, last_name)

                            # send to findMatch, add set of names to patient object in name_on_google
                            # first open google reviews file and turn it into list of objects

                            google_name = findMatch(name_variations, data)
                            patient['name_on_google'] = google_name
                            # if we have a match or potential matches, place in potential_matches list
                            if google_name != "":
                                patient['wrote_review'] = 1
                                potential_matches.append(patient)
                            # otherwise place in no_matches list
                            else:
                                no_matches.append(patient)

                # add this filename to our already_scraped file set
                scraped.add(filename)

    # add scraped to already_scraped
    f.write('\n'.join(str(p) for p in scraped))
    f.close()
    f1.close()
    return potential_matches, no_matches

def generatePatientObj(name, sheet, phone, email):
    return {
        'name': name,
        'excel_sheet' : sheet,
        'phone' : phone,
        'email' : email,
        'wrote_review' : 0,
        'name_on_google' : ""
    }

def getPatientInfo(i, sheet, first, last, email, phone):
    first_name = sheet[i][first].value
    last_name = sheet[i][last].value
    email_address = sheet[i][email].value
    phone_number = sheet[i][phone].value
    return first_name, last_name, email_address, phone_number


def findMatch(names, google_reviews):
    potentials = ""
    for i, review in enumerate(google_reviews):
        google_name = review['name'].lower()
        if google_name in names:
            potentials = google_name
    return potentials

def generateNames(first, last):
    variations = set()
    nickname = None
    if "\"" in first or "\'" in first:  # check for nickname
        indexes = [x for x, v in enumerate(first) if (v == "\'" or v == "\"")]
        name = first[:indexes[0]]
        nickname = first[indexes[0] + 1 : indexes[1]]
    if last is not None:
        variations.add((first + ' ' + last).lower())
        variations.add((first + ' ' + last[0]).lower())
        if nickname is not None:
            variations.add((nickname + ' ' + last).lower())
            variations.add((nickname + ' ' + last[0]).lower())
    return variations

if __name__ == '__main__':
    # run getPatients
    potential_matches, no_matches = getPatients()
    # from results, write into db no_matches and potential_matches

    DB_URL = 'http://127.0.0.1:5000/patients'
    for patient in potential_matches:
        r = requests.post(DB_URL, json=patient)
        print(r.text)
    for patient in no_matches:
        r1 = requests.post(DB_URL, json=patient)
        print(r1.text)


