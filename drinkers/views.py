from django.shortcuts import render, render_to_response
from django.template import RequestContext
from drinkers.forms import DrinkerForm
from django.views.generic.edit import FormView
from lib.arduino_reader import ArduinoReader
from lib.drink_action import DrinkAction


class DrinkerView(FormView):
    template_name='main.html'
    form_class=DrinkerForm
    success_url='/recomendation/'
    
    def form_valid(self, form):
        drinker = form.to_drinker()
        measurements = ArduinoReader().estimate_blood_alcohol_concentration(5)
        action = DrinkAction(drinker, measurements)
        
        return render_to_response('recommendation.html', { 'action' : action }, 
                    context_instance=RequestContext(self.request))
