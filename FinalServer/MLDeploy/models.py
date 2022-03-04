from django.db import models

class TweetRequest(models.Model):
    category = models.CharField(max_length=32)
    def __str__(self):
        return self.category