from django.shortcuts import render
from drinkers.forms import DrinkerForm
from django.views.generic.edit import FormView

class DrinkerView(FormView):
    template_name='drinker.html'
    form_class=DrinkerForm
    success_url='/recomendation/'
    
    def form_valid(self, form):
        drinker = form.to_drinker()
        measurements = ArduinoReader().get_measurements()
        action = DrinkAction(drinker, measurements
        
        return render_to_response('recommendation.html', { 'action' : action }, 
                    context_instance=RequestContext(self.request))
