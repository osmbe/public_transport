from django.db import models

class Operator(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    language_iso = models.CharField(max_length=50)
