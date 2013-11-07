from django.db import models


class Drinker(models.Model):
    weight = models.IntegerField()
    gender = models.BooleanField()
    hunger = models.IntegerField()
    tolerance = models.IntegerField()

ACTION_TYPES = (
    ('sober', 'Sober'),
    ('beer', 'Beer'),
    ('wine', 'Wine'),
    ('liquor', 'Liquor'),
)


class Recommendation(models.Model):
    action_type = models.CharField(max_length=255, choices=ACTION_TYPES)
    name = models.CharField(max_length=255)
    alcohol_percentage = models.DecimalField(decimal_places=2, max_digits=5)
