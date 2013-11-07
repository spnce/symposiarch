from django import forms
from drinkers.models import Drinker


class DrinkerForm(forms.Form):
    weight = forms.IntegerField(min_value=0)
    male = forms.BooleanField
    hunger = forms.IntegerField(min_value=0)
    tolerance = forms.IntegerField(min_value=0,max_value=10)

    def to_drinker(self):
        return Drinker(weight=self.weight, gender=self.gender, hunger=self.hunger, tolerance=self.tolerance)
