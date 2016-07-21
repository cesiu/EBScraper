**EBScraper** is a set of Python scripts that attempts to automate the task of
indexing (saving images of and links to) LEGO creations posted on the 
Eurobricks Star Wars forum and its subforums. 



######Dependencies######
EBScraper is written for Python 2. It requires Beautiful Soup 4 for parsing
HTML files (to extract information about topics and posts), Selenium for 
interacting with websites through a browser (to post the results to the forum),
Pillow for processing images (to generate thumbnails), and imguru for uploading
images. At the moment, EBScraper is hardcoded to use bash commands and imguru, 
which is an OS X C++ program.



######Use######
**eb_scraper.py** scans the first page (the first thirty topics) of EB's Star
Wars forum. It identifies all topics it thinks are LEGO creations that are 
ready for indexing (i.e., not works-in-progress and not already indexed), 
downloads the first non-emoticon image it finds in those topics, generates 
thumbnails, and saves the topic name, URL, author, and image URL.

Usage: `pypy eb_scraper.py [page min] [page max] <options>`

Options:
- -i - Generate a thumbnail and upload it to imgur.
- -c - Automatically classify creations instead of asking for confirmation.
- -m - Include topics listed as modifications of LEGO sets.



**renderer.py** takes the information saved by `eb_scraper`, translates it into
BBCode, and posts it to a topic on EB (using credentials provided in an
external file).

Usage: `pypy renderer.py <options>`

Options:
- -u - Upload the rendered BBCode to specified EB posts.
- -d - Dev mode. Run the renderer even if the entries have no image URLs.



**classifier.py** is an experimental class that uses some very simple machine
learning to attempt to figure out how to classify a creation by determining the 
Star Wars era (Original Trilogy, Expanded Universe, etc.) and the type 
(vehicle, diorama, etc.) it pertains to. The classifier is used by the scraper, 
not as a standalone program. `pypy classifier.py` will give the option of 
resetting the saved classification data.
