from django.shortcuts import redirect, render
import requests
import sys
from subprocess import run, PIPE
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

FILEPATH_REQUESTREVIEWS = ''  # absolute path on local machine to image.py
FILEPATH_REQUESTAGAIN = ''  # absolute path on local machine to requestAgain.py
FILEPATH_SCRAPEGOOGLE = ''  # absolute path on local machine to scrapeGoogle.py

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid:
            user = form.get_user()
            login(request, user)
            return redirect('home/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form' : form})

def logout_view(request):
    logout(request)
    return render(request, 'login.html')

@login_required(login_url="/login/")
def button(request):
    return render(request, 'home.html')


def external(request):
    """
        calls on external image.py script to request reviews from input on selected excel sheet
        returns nothing, simply runs script

    """
    image = request.FILES['image']
    print("image is ", image)
    fs = FileSystemStorage()
    filename = fs.save(image.name, image)
    fileurl = fs.open(filename)
    templateurl = fs.url(filename)
    image = run([sys.executable, FILEPATH_REQUESTREVIEWS, str(fileurl), str(filename)], shell = False, stdout = PIPE)
    return render(request, 'home.html', {'raw_url': templateurl, 'edit_url': image.stdout.decode('utf8')})

def requestAgain(request):
    """
        calls on external script requestAgain.py that sends review requests after scraping google reviews
        returns nothing, simply runs script
    """
    out = run([sys.executable, FILEPATH_REQUESTAGAIN], shell = False, stdout = PIPE)
    return render(request, 'home.html')

def scrapeGoogle(request):
    """
        calls on external script scrapeGoogle.py that scrapes google reviews and crosschecks with patient db
        returns nothing, simply runs script
    """
    out = run([sys.executable, FILEPATH_SCRAPEGOOGLE], shell = False, stdout = PIPE)
    return render(request, 'home.html')