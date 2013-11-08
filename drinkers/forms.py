from django import forms
from django.forms import RadioSelect
from drinkers.models import Drinker, DRINK_PREFERENCES

MALE_CHOICES = (
    ('True', 'Male'),
    ('False', 'Female'),
)

class DrinkerForm(forms.Form):
    name = forms.CharField(max_length=50)
    weight = forms.IntegerField(min_value=0)
    male = forms.ChoiceField(widget=RadioSelect(), choices=MALE_CHOICES, initial=True)
    hunger = forms.IntegerField(min_value=0)
    tolerance = forms.IntegerField(min_value=0,max_value=10)
    drink_preference = forms.ChoiceField(choices=DRINK_PREFERENCES)

    def to_drinker(self):
        return Drinker(
            name=self.cleaned_data['name'],
            weight=self.cleaned_data['weight'],
            gender=self.cleaned_data['male'],
            hunger=self.cleaned_data['hunger'],
            tolerance=self.cleaned_data['tolerance'],
            drink_preference=self.cleaned_data['drink_preference']
        )
