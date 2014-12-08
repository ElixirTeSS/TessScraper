TessScraper
===========

This is a prototype of a python script which can be used to scrape html from websites and upload the content to a CKAN installation. 

Installation
============

    git clone git@github.com:ElixirUK/TessScraper.git
    pip install -r requirement.txt

On your TeSS instance locate the API key from your user account page and copy it into a file called 'api.txt' in the root directory of TessScraper. It should look something similar to this:

    2204e6c5-d011-4aec-8005-5b1243159aed

If you are not using the https://tess.oerc.ox.ac.uk deployment of TeSS be sure to configure the uploader to the correct urls/protocols of your deployment in the training/upload.py file.


Usage
==========

    python goblet_scraper.py
    python soc_scraper.py
    python genome3d_scraper.py
    python ebi_scraper.py
