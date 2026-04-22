from django.db import models


class Book(models.Model):
    id = models.BigAutoField(primary_key=True)
    isbn = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year = models.PositiveIntegerField()

    def __int__(self):
        return self.id


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, default='DefaultUser')
    email = models.EmailField(max_length=254, null=False, unique=True)
    password = models.CharField(max_length=20, null=False)

    def __int__(self):
        return self.id


class Review(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField(null=False)
    book_id = models.IntegerField(null=False)
    review = models.CharField(max_length=2000)
    rating = models.IntegerField()

    def __int__(self):
        return self.id

