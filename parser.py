#!/usr/bin/env python

import xlrd
import re

# WORK IN PROGRESS:
# TODO:
# 1. Finish it. ;-)
# 2. Refactor to give "Theme" and "Tutorial" objects, add tutorials to themes.

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
excel_file = 'Template for TeSS_EMBL EBI.xlsx'

workbook = xlrd.open_workbook(excel_file)
for sheet in workbook.sheets():
    # Parsing should be different for the final sheet, for the column headers aren't the same
    # as those listed above. FRC.
    title =  sheet.name
    if not title:
        continue
    if 'face to face course' in title.lower():
        # in future, run some different parsing here
        continue
    print "Title: " + title
    current_row = 1

    # go down the first column looking for entries
    while current_row < sheet.nrows:
        tutorial_name = sheet.cell_value(current_row,0)
        # empty row
        if not tutorial_name:
            current_row += 1
            continue
        # start of users annotations
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
        print "Tutorial name: " + tutorial_name
        print "URL: " + url
        print "Follows: " + follows
        # resources may have several entries
        resources = []
        res_row = current_row
        res = sheet.cell_value(res_row,3)
        while res:
            resources.append(res)
            if res_row == (sheet.nrows - 1):
                break
            res_row += 1
            res = sheet.cell_value(res_row,3)
        print "Resources: " + str(resources)
        doi = sheet.cell_value(current_row,4)
        print "DOI: " + doi
        keywords = []
        kw_row = current_row
        kw = sheet.cell_value(kw_row,5)
        while kw:
            for w in kw.split(","):
                keywords.append(w)
            if kw_row == (sheet.nrows - 1):
                break
            kw_row += 1
            kw = sheet.cell_value(kw_row,5)
        print "Keywords: " + str(keywords)




        print "\n"
        current_row += 1


"""
    worksheet = workbook.sheets()[0] # 1 for production, 2 for test
    num_rows = worksheet.nrows - 1
    #num_cells = worksheet.ncols - 1
    curr_row = 1 # row 0 is to be discarded
    print "NUM_ROWS: " + str(num_rows)
    while curr_row <= num_rows:
        full_name =  worksheet.cell_value(curr_row,0).encode('utf8')
        #abbreviation = worksheet.cell_value(curr_row,1)
        #if not abbreviation:
        #    abbreviation = "No abbreviation"
        link = worksheet.cell_value(curr_row,6)
        if not re.search('biosharing', link):
            #print str(link.rsplit('/',1)[-1].encode('utf8'))#  + "," + str(contact_details.encode('utf8'))
            curr_row += 1
            continue
        claimed = worksheet.cell_value(curr_row,1).encode('utf8')
        responded = worksheet.cell_value(curr_row,2).encode('utf8')
        contact_details = worksheet.cell_value(curr_row,7).encode('utf8')
"""
