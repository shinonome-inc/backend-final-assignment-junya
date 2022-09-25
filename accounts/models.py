# from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=254)


# class Article(models.Model):
#     author = models.ForeignKey(
#         get_user_model(),
#         on_delete=models.CASCADE,
#     )

# class FriendShip(models.Model):
#     pass
