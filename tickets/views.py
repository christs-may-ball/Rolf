from django import forms
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from math import ceil
import stripe

from . import forms
from .models import Request
from . import constants

def index(request):
    if request.user.is_authenticated():
        if hasattr(request.user, 'detail'):
            requests = Request.objects.filter(user=request.user).exclude(status='C')
            if request.user.detail.charity:
                request.user.detail.charity = Request.objects.filter(user=request.user, status__in=['H', 'P', 'S', 'Q', 'D']).count()*constants.PRICE_CHARITY
                request.user.detail.save()
            cost = request.user.detail.charity + Request.objects.filter(user=request.user, status__in=['P', 'S']).count()*constants.PRICE_TICKET + Request.objects.filter(user=request.user, status='Q').count()*constants.PRICE_QUEUE + Request.objects.filter(user=request.user, status='D').count()*constants.PRICE_DINING + Request.objects.filter(user=request.user, status='H').count()*constants.PRICE_HALF
            postage = constants.PRICE_POSTAGE if request.user.detail.address and cost else 0
            owe = max(0, cost + postage - request.user.detail.balance)
            if Request.objects.filter(status__in=['S', 'Q', 'D']).exclude(priority='ST').count() >= (constants.LIMIT_STUDENT + constants.LIMIT_ALUMNI) and request.user.detail.college != 'Sta':
                owe = 0
            stripe_owe = ceil(((owe + 0.2)/0.986)*100)
            processing = (stripe_owe - owe*100)//1/100
            return render(request, 'tickets/tickets.html', {
                'requests': requests,
                'other_request': Request.objects.filter(ticket_crsid=request.user.username, status__in=['H', 'S', 'Q', 'D']).exclude(user=request.user).first(),
                'more': len(requests) < constants.LIMIT_PERSON,
                'avail_queue': Request.objects.filter(status='Q').count() < constants.LIMIT_QUEUE,
                'avail_dining': Request.objects.filter(status='D').count() < constants.LIMIT_DINING,
                'cost': cost,
                'owe': owe,
                'stripe': stripe_owe,
                'processing': processing,
                'postage': postage,
                'ref': ("{0:x}".format(10000 + request.user.pk) + 'Z' + request.user.last_name + request.user.first_name)[:8].upper(),
                'email': request.user.email,
            })
        else:
            return HttpResponseRedirect('accounts/details/')
    else:
        return render(request, 'tickets/index.html', {})

def login(request):
    if request.method == "POST":
        form = auth.forms.AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return HttpResponseRedirect("/")
    else:
        form = auth.forms.AuthenticationForm(request)

    return render(request,  request.path.split("/")[1] + "/login.html", {
        'form': form,
    })

def register(request):
    if request.method == "POST":
        form = forms.AlumniForm(data=request.POST)
        if form.is_valid():
            if (form.save()):
                return HttpResponseRedirect("/alumni/success/")
            else:
                return HttpResponseRedirect("/alumni/failure/")
    else:
        form = forms.AlumniForm()

    return render(request, "alumni/register.html", {
        'form': form,
    })

def register_staff(request):
    if request.method == "POST":
        form = forms.StaffForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/staff/login/")
    else:
        form = forms.StaffForm()

    return render(request, "staff/register.html", {
        'form': form,
    })

def success(request):
    return render(request, "alumni/success.html", {})

def failure(request):
    return render(request, "alumni/failure.html", {})

def admin_redirect(request):
    return HttpResponseRedirect("/accounts/login/")

def details(request):
    if hasattr(request.user, 'detail'):
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = forms.DetailsForm(data=request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect("/")
    else:
        form = forms.DetailsForm()

    return render(request, "alumni/details.html", {
        'form': form,
    })


def request(request):
    if Request.objects.filter(user=request.user).exclude(status='C').count() >= constants.LIMIT_PERSON:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = forms.RequestForm(data=request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect("/")
    else:
        form = forms.RequestForm()

    return render(request, "tickets/request.html", {
        'form': form,
    })

def queue(request, pk):
    ticket_request = get_object_or_404(Request, pk=pk)
    if (request.user == ticket_request.user
        and ticket_request.status == 'S'
        and Request.objects.filter(status='Q').count() < constants.LIMIT_QUEUE):
        ticket_request.status = 'Q'
        ticket_request.save()

    return HttpResponseRedirect("/")


def dining(request, pk):
    ticket_request = get_object_or_404(Request, pk=pk)
    if (request.user == ticket_request.user
        and ticket_request.status in ('S', 'Q')
        and Request.objects.filter(status='D').count() < constants.LIMIT_DINING):
        ticket_request.status = 'D'
        ticket_request.save()

    return HttpResponseRedirect("/")

def charity(request):
    if request.user.detail.charity == 0:
        request.user.detail.charity = Request.objects.filter(user=request.user, status__in=['H', 'S', 'Q', 'D']).count()*constants.PRICE_CHARITY
    else:
        request.user.detail.charity = 0
    request.user.detail.save()
    return HttpResponseRedirect("/")

def standard(request, pk):
    ticket_request = get_object_or_404(Request, pk=pk)
    if (request.user == ticket_request.user
        and ticket_request.status == 'H'):
        ticket_request.status = 'S'
        ticket_request.save()

    return HttpResponseRedirect("/")

def name(request, pk):
    ticket_request = get_object_or_404(Request, pk=pk)
    if (request.user != ticket_request.user):
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = forms.NameForm(data=request.POST)
        if form.is_valid():
            if request.user.detail.college == 'Sta':
                form.save(ticket_request)
                return HttpResponseRedirect("/")
            else:
                return render(request, "tickets/name_pay.html", {
                    'form': form,
                    'pk': pk,
                    'email': request.user.email,
                })
    else:
        form = forms.NameForm()

    return render(request, "tickets/name.html", {
        'form': form,
        'pk': pk,
    })

def namepay(request, pk):
    ticket_request = get_object_or_404(Request, pk=pk)
    if (request.user != ticket_request.user):
        return HttpResponseRedirect("/")
    stripe.api_key = "DON'T POST SECRET KEYS TO GITHUB"
    token = request.POST['stripeToken']
    form = forms.NameForm(data=request.POST)
    if form.is_valid():
        try:
            charge = stripe.Charge.create(
                amount=2000,
                currency="gbp",
                source=token,
                description="Name Change Payment",
                receipt_email=request.user.email,
            )
            form.save(ticket_request)
            print (":?")
        except stripe.error.CardError as e:
            return HttpResponseRedirect("/tickets/payment_error/")
    return HttpResponseRedirect("/")

def confirm(request, confirmation, pk):
    ticket_request = get_object_or_404(Request, pk=pk)
    if (request.user != ticket_request.user):
        return HttpResponseRedirect("/")

    return render(request, "tickets/confirm.html", {
        'confirmation': confirmation + '/' + pk,
    })

def pay(request):
    stripe.api_key = "DON'T POST SECRET KEYS TO GITHUB"
    token = request.POST['stripeToken']

    cost = request.user.detail.charity + Request.objects.filter(user=request.user, status__in=['P', 'S']).count()*constants.PRICE_TICKET + Request.objects.filter(user=request.user, status='Q').count()*constants.PRICE_QUEUE + Request.objects.filter(user=request.user, status='D').count()*constants.PRICE_DINING + Request.objects.filter(user=request.user, status='H').count()*constants.PRICE_HALF
    postage = constants.PRICE_POSTAGE if request.user.detail.address and cost else 0
    owe = max(0, cost + postage - request.user.detail.balance)
    stripe_owe = ceil(((owe + 0.2)/0.986)*100)

    try:
        charge = stripe.Charge.create(
            amount=stripe_owe,
            currency="gbp",
            source=token,
            description="Ticket Payment",
            receipt_email=request.user.email,
        )
        request.user.detail.balance += owe
        request.user.detail.save()
        for ticket in Request.objects.filter(user=request.user, status='P'):
            ticket.status = 'S'
            ticket.save()
    except stripe.error.CardError as e:
        return HttpResponseRedirect("/tickets/payment_error/")

    return HttpResponseRedirect("/")

def payment_error(request):
    return render(request, "tickets/payment_error.html", {})
