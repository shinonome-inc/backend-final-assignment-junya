from django.conf import settings
from django.db import models


class Tweet(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.content)

    class Meta:
        ordering = ["-created_at"]
