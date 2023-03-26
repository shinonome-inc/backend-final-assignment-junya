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


class FriendShip(models.Model):
    follower = models.ForeignKey(User, related_name="follower", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_friendship"),
        ]
