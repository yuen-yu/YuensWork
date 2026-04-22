from .forms import LogonForm, RegisterForm, SearchForm, ReviewForm
from .models import Book, User, Review

from django.db import transaction, IntegrityError
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from dotenv import load_dotenv

import csv, requests, os

load_dotenv()       # This loads the variables from .env


def addReview(request):
    if (request.method == "POST"):
        form = ReviewForm(request.POST) # Bind the submitted data
        if form.is_valid():
            # Process the clean data
            text = form.data['review']
            select = form.data['rating']
            try:
                newReview = Review.objects.create(user_id=int(request.session['userid']), book_id=int(request.session['bookid']), review=text, rating=select)
                messages.success(request, "Review added successful!")
                return render(request, 'BookReviewApp/search.html')
            except Exception as e:
                print(f"Add review error: {e}")
                errmsg = f"{type(e).__name__} - {e}"
                messages.error(request, errmsg)
                return render(request, 'BookReviewApp/search.html')
        else:
             errmsg = f"Invalid Review inputs"
             messages.error(request, errmsg)
             return render(request, 'BookReviewApp/search.html')


def book(request, id):
    try:
        book = Book.objects.get(id=id)
        request.session['bookid'] = book.id

        count, rating, reviews, btnRequired = bookInfo(request, book.isbn)

        context = {'book' : book,
                   'count' : count,
                   'rating' : rating,
                   'reviews' : reviews,
                   'btnRequired' : btnRequired}

        return render(request, 'BookReviewApp/book.html', context)

    except Book.DoesNotExist:
        print(f"Book name : {book.name} does not exist.")
        errmsg = f"Book does not exist"
        raise Http404("Book does not exist")
    except Exception as e:
        errmsg = f"{type(e).__name__} - {e}"
        messages.error(request, errmsg)
        return render(request, 'BookReviewApp/search.html')


def books(request):
    form = SearchForm(request.POST)
    if form.is_valid():
        # Process the clean data
        isbn = form.data['isbn']
        title = form.data['title']
        author = form.data['author']
        try:
            context = {"books" : filter_records(isbn, title, author)}
            #request.session['context'] = context
            return render(request, 'BookReviewApp/books.html', context)
        except Exception as e:
            print(f"An exception occurred: {type(e).__name__}")
            print(f"Books: {e}")
            errmsg = f"{type(e).__name__} - {e}"
            messages.error(request, errmsg)
            return redirect('search')                
    else:
        messages.error(request,'Invalid Search Form.')
        return redirect('search')


#Get count and rating from google books api
def bookInfo(request, isbn): 
    API_ENDPOINT = 'https://www.googleapis.com/books/v1/volumes'
    API_KEY = os.getenv("Google_Books_Key")
    rating = 0
    count = 0

    headers = {
        "User-Agent": API_KEY, 
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    reviews = Review.objects.filter(book_id=int(request.session['bookid'])).values_list('review')
    
    btnRequired = True

    if Review.objects.filter(book_id=int(request.session['bookid']),user_id=int(request.session['userid'])).exists():
        btnRequired = False

    params = {'q': f'isbn:{isbn}'} 
    try:
        print(f"Trying ISBN: {isbn}")
        print(f"API_ENDPOINT: {API_ENDPOINT}")
        print(f"params: {params}")
        res = requests.get(API_ENDPOINT, params=params, headers=headers)
        data = res.json()
        print(f"data: {data}")
        if 'items' in data:
            book_info = data['items'][0]['volumeInfo']
            rating = book_info.get('averageRating')
            count = book_info.get('ratingsCount')           
    except requests.exceptions.RequestException as e:
        print(f"BookInfo error: {e}")
    return count, rating, reviews, btnRequired


def filter_records(isbn, title, author):
    # Start with the base queryset
    queryset = Book.objects.all()

    # Add filters only if the input is not empty (checks for None or empty string '')
    if isbn:
        # Use appropriate field lookups (e.g., __icontains, __exact, etc.)
        queryset = queryset.filter(isbn__icontains=isbn)

    if title:
        queryset = queryset.filter(title__icontains=title)

    if author:
        queryset = queryset.filter(author__icontains=author)

    # The final queryset will only include records that satisfy all non-empty conditions
    return queryset
    # data = serializers.serialize('json', queryset)
    # return HttpResponse(data, content_type='application/json')
    

def index(request):
     if not Book.objects.exists():

        # Ensure you have the correct path to your CSV file
        file_path = 'books.csv'

        # Use a transaction to ensure all or none of the data is imported
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            objects_to_create = []
    
            for row in reader:
                # Assuming CSV headers match model field names
                objects_to_create.append(Book(**row))

             # Use transaction.atomic() to ensure atomicity for the bulk operation
            with transaction.atomic():
                Book.objects.bulk_create(objects_to_create)        

     #return render(request, 'BookReviewApp/index.html')
     if 'userid' in request.session:
         form = SearchForm()
         return render(request, 'BookReviewApp/search.html', {'form': form})
     else:
         return render(request, 'BookReviewApp/index.html')


def logon(request):
    #A user is logged in, redirect to the Search page
    if ((request.method == "GET") and ('userid' in request.session)):
        #return redirect(request, 'BookReviewApp/search.html')
        form = SearchForm()
        return render(request, 'BookReviewApp/search.html', {'form': form})
    
    if (request.method == "GET"):
        #return render(request, 'BookReviewApp/logon.html')
        form = LogonForm() # Display an empty form for GET requests
        return render(request, 'BookReviewApp/logon.html', {'form': form})

    # Choose add a new user from the Logon page
    if ((request.method == "POST") and ("ButtonRegister" in request.POST)):
        return render(request, 'BookReviewApp/register.html')
    
    if request.method == 'POST':
        form = LogonForm(request.POST) # Bind the submitted data
        if form.is_valid():
            # Process the clean data
            email = form.data['email']
            password = form.data['password']
            try:
                aUser = User.objects.get(email = email, password = password)
                request.session['userid'] = aUser.id
                return render(request, 'BookReviewApp/search.html')
            except Exception as e:
                print(f"An exception occurred: {type(e).__name__}")
                print(f"Logon: {e}")
                errmsg = f"Either User - {email} not exist OR Invalid password."
                messages.error(request, errmsg)
                return redirect('logon')
        else:
            return render(request, 'BookReviewApp/logon.html')
    #else:
    #    form = LogonForm() # Display an empty form for GET requests
    #    return render(request, 'BookReviewApp/logon.html', {'form': form})


def logout(request):
    request.session.clear()
    return redirect('index')


def register(request):
    if (request.method == "GET"):
        form = RegisterForm()
        return render(request, 'BookReviewApp/register.html', {'form': form})

    if request.method == 'POST':
        form = RegisterForm(request.POST) # Bind the submitted data
        if form.is_valid():
            # Process the clean data
            name = form.data['name']
            email = form.data['email']
            password = form.data['password']
            try:
                newUser = User.objects.create(name = name, email = email, password = password)
                msg = f"User : {name} registered successful. Logon to access."
                messages.success(request,msg)
                return redirect('logon')
            except IntegrityError as e:
                print(f"An exception occurred: IntegrityError")
                print(f"Register: User already exist")
                errmsg = f"Same user already exist in the system"
                messages.error(request, errmsg)
                return redirect('register')           
            except Exception as e:     #if an error occurs
                print(f"An exception occurred: {type(e).__name__}")
                print(f"Register: {e}")
                errmsg = f"{type(e).__name__} - {e}"
                messages.error(request, errmsg)
                return redirect('register')            
        else:
            messages.error(request,'Invalid Register Form.')
            return redirect('register')
    

def search(request):
    if 'userid' in request.session:
        form = SearchForm()
        return render(request, 'BookReviewApp/search.html', {'form': form})
    else:
        #return render_template("logon.html")
        return redirect('logon')
