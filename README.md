# Google Review Manager

A django web app for requesting google reviews from clients via text and email, using a flask REST api with client information, updated with the aid of a web scraper to update client review status. Such automation has increased google review counts for an ABQ doctor's office by 250% in 4 months.


## Flask server
### --- to run locally, in server/api:
source .venv/bin/activate
export FLASK_APP=application.py
export FLASK_ENV=development
flask run

## Django app 
views.py - modify filepaths
image.py, requestAgain.py - edit user info for text/email, and directly modify messages if desired

### --- to run locally, in app/buttonpython:
python manage.py runserver 127.0.0.1:8002

