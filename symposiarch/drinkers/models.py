from django.db import models

class Drinker(models.Model):
    weight = models.IntegerField
    gender = models.BooleanField
    hunger = models.IntegerField
    tolerance = models.IntegerField

