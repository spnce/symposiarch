from decimal import Decimal
from django.http import HttpResponse
from django.template import loader, RequestContext
from symposiarch.lib.arduino_reader import ArduinoReader


def index(request):
    template = loader.get_template('step1.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


def sampling(request):
    template = loader.get_template('step2.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


def start_sampling(request):
    template = loader.get_template('bac_estimate.json')
    ar = ArduinoReader()
    context = RequestContext(request, {
        'bac': ar.estimate_blood_alcohol_concentration(Decimal(request.GET.get('seconds', 5.0)))
    })
    return HttpResponse(template.render(context))


def recommendation(request):
    template = loader.get_template('step3.html')
    context = RequestContext(request, {
        'bac': Decimal(request.GET.get('bac', 0))
    })
    return HttpResponse(template.render(context))
