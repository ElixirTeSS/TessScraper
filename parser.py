#!/usr/bin/env python

import xlrd
import re

from training import *

# WORK IN PROGRESS
# Before going any further, a collection object is required in order to store the tutorials.
website = CourseWebsite();

# A script to parse an Excel file of tutorials prior to importing into CKAN.
# Documentation for the sheet class is here:
# https://secure.simplistix.co.uk/svn/xlrd/trunk/xlrd/doc/xlrd.html?p=4966#sheet.Sheet-class
# Headers:
# 0: Name of tutorial
# 1: URL
# 2: Name of tutorial  it follows on from
# 3: links to resources / tools used
# 4: DOI
# 5: Keywords
# 6: Name of author
# 7: Date created
# 8: Date of last update
# 9: Difficulty rating out of 5 stars
# N.B. the layout of this file is such that it is best suited for viewing by a human rather than parsing; therefore
# one will have to carefully loop over the first column to find where entries have been placed and use the index
# of this to investigate the other columns, counting down the rows therefrom until a blank one is found.


# This bit is to get the id of a lesson which matches the passed in name, and return the
# uuid thereof for the purposes of storage.
def get_parent_id(name,lessons):
    for l in reversed(lessons):
        if l.name == name:
            return l.id
    return None

# parse the excel file
excel_file = 'Template for TeSS_EMBL EBI.xlsx'
workbook = xlrd.open_workbook(excel_file)
for sheet in workbook.sheets():
    # Parsing should be different for the final sheet, for the column headers aren't the same
    # as those listed above. FRC.
    face_to_face = False
    title =  sheet.name
    if not title:
        continue
    if 'face to face course' in title.lower():
        face_to_face = True
    print "Title: " + title
    current_row = 1

    # go down the first column looking for entries
    while current_row < sheet.nrows:

        # Look in courses.py to see the difference between a tutorial and a face-to-face course.
        if face_to_face:
            tut = FaceToFaceCourse()
            # continue here; simply creating the web courses will do for testing purposes.
            current_row += 1
            continue
        else:
            tut = Tutorial()

        tutorial_name = sheet.cell_value(current_row,0)
        # empty row
        if not tutorial_name:
            current_row += 1
            continue
        # Start of users annotations:
        # At this point the collection objects attributes should be fully populated.
        if "for collection of tutorials" in tutorial_name.lower()\
                or "name of website" in tutorial_name.lower()\
                or "link to website" in tutorial_name.lower()\
                or "elixir uk sector" in tutorial_name.lower():
            current_row +=1
            continue

        # ...at this point we should be carrying on with parsing the data for an actual class
        url = sheet.cell_value(current_row,1)
        follows = sheet.cell_value(current_row,2)
        # print these for now - later, store in a tutorial object
        tut.name = tutorial_name
        tut.url = url
        if not face_to_face:
            tut.parent_id = get_parent_id(follows,website.tuition_units)
        #print "Follows: " + follows

        # resources may have several entries
        res_row = current_row
        res = sheet.cell_value(res_row,3)
        while res:
            tut.resources.append(res)
            if res_row == (sheet.nrows - 1):
                break
            res_row += 1
            res = sheet.cell_value(res_row,3)

        tut.doi = sheet.cell_value(current_row,4)

        kw_row = current_row
        kw = sheet.cell_value(kw_row,5)
        while kw:
            for w in kw.split(","):
                tut.keywords.append(w)
            if kw_row == (sheet.nrows - 1):
                break
            kw_row += 1
            kw = sheet.cell_value(kw_row,5)

        ##################################################################
        # sheet layout changes at this point depending whether we've got #
        # tutorials on-line or face-to-face classes                      #
        ##################################################################
        if face_to_face:
            # gather all the organisers and append them to the organisers array
            pass
        else:
            tut.author = sheet.cell_value(current_row,6)

        if face_to_face:
            # split dates on "-", perhaps, and append to array
            pass
        else:
            created = sheet.cell_value(current_row,7)
            if created:
                tut.created = str(xlrd.xldate_as_tuple(created, workbook.datemode))
            else:
                tut.created = "NONE"

        if face_to_face:
            # there is no "last updated" for a face-to-face tutorial
            pass
        else:
            last_update = sheet.cell_value(current_row,8)
            if last_update:
                tut.last_update = str(xlrd.xldate_as_tuple(last_update, workbook.datemode))
            else:
                tut.last_update = "NONE"

        if face_to_face:
            tut.difficulty = sheet.cell_value(current_row,8)
        else:
            tut.difficulty = sheet.cell_value(current_row,9)

        # If this is a tutorial, store it in the website collection:
        if face_to_face:
            print "F-2-F: " + tut.name
        else:
            website.tuition_units.append(tut)


        current_row += 1

    print "Web: " + str(website)
    website.list_names()


