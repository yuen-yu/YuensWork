from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('logon', views.logon, name='logon'),
    path('register', views.register, name='register'),
    path('search', views.search, name='search'),
    path('books', views.books, name='books'),
    path('book/<int:id>/', views.book, name='book'),
    path('logout', views.logout, name='logout'),
    path('addReview', views.addReview, name='addReview'),
]