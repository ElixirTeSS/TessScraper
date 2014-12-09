TessScraper
===========

This is a prototype of a python script which can be used to scrape html from websites and upload the content to a CKAN installation. 

Installation
============

    git clone git@github.com:ElixirUK/TessScraper.git
    cd TessScraper
    sudo pip install -r requirements.txt

You will need to edit the configuration file, which by default is called 'uploader_config.txt'. An example file is provided, and it should reside in the root directory of TessScraper.

On your TeSS instance locate the API key from your user account page and copy it into the configuration file. It should look something similar to this:

    2204e6c5-d011-4aec-8005-5b1243159aed

If you are not using the https://tess.oerc.ox.ac.uk deployment of TeSS be sure to configure the uploader to the correct urls/protocols of your deployment in the configuration file.


Usage
==========

    python goblet_scraper.py
    python soc_scraper.py
    python genome3d_scraper.py
    python ebi_scraper.py
