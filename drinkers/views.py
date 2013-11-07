from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.template import RequestContext
from drinkers.forms import DrinkerForm
from django.views.generic.edit import FormView
from drinkers.models import Recommendation
from lib.arduino_reader import ArduinoReader
from lib.drink_action import DrinkAction

STANDARD_PERCENT_ALCOHOL = {
    'beer': 5.0,
    'wine': 12.0,
    'liquor': 40.0
}

class DrinkerView(FormView):
    template_name = 'main.html'
    form_class = DrinkerForm
    success_url = reverse_lazy('recommendation')

    def form_valid(self, form):
        drinker = form.to_drinker()
        bac = ArduinoReader(None).read(5)
        action = DrinkAction(drinker, bac)
        num_drinks = action.get()
        # convert num_drinks to alcohol percentage
        preferred_drink_alcohol = STANDARD_PERCENT_ALCOHOL.get(drinker.drink_preference)
        percent_alcohol = num_drinks * preferred_drink_alcohol
        # figure out what drink(s) to load?
        recommendations = Recommendation.objects.raw(
            '''SELECT d.* FROM drinkers_recommendation d
               WHERE ABS(d.alcohol_percentage - %s) = (
                SELECT MIN(ABS(d2.alcohol_percentage - %s))
                FROM drinkers_recommendation d2
            )''',
            [percent_alcohol, percent_alcohol]
        )
        # pick one at random
        rec = None
        for recommendation in recommendations:
            rec = recommendation

        return render_to_response('recommendation.html', {'recommendation': rec},
                                  context_instance=RequestContext(self.request))
