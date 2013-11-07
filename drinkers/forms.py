from django import forms

class DrinkerForm(forms.Form):
    weight = forms.IntegerField(min_value=0)
    male = forms.BooleanField
    hours_since_meal = forms.IntegerField(min_value=0)
    tolerance = forms.IntegerField(min_value=0,max_value=10)

    def to_drinker(self):
        return Drinker(weight, gender, hunger, tolerance)
