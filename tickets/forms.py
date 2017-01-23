from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from . import constants
from .models import Detail, Alumni, Request

class AlumniForm(UserCreationForm):
    username = forms.EmailField(required=True, label="Email address")
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    address = forms.CharField(max_length=200, required=True)
    matriculation_year = forms.ChoiceField(choices=[(year, year) for year in range(1931, 2015)[::-1]])
    tripos = forms.CharField(max_length=100, required=False)
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1912, 1998)[::-1]), required=True, label="Date of birth")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "address")

    def save(self):
        if not Alumni.objects.filter(
            matriculation_year=self.cleaned_data["matriculation_year"],
            dob=str(self.cleaned_data["dob"]),
        ).exists():
            return False

        user = super(AlumniForm, self).save(commit=False)
        user.email = user.username
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        user_details = Detail(user=user, address=self.cleaned_data["address"], college='Alu')
        user_details.save()
        return True

class StaffForm(UserCreationForm):
    username = forms.EmailField(required=True, label="Email address")
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")

    def save(self):
        user = super(StaffForm, self).save(commit=False)
        user.email = user.username
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        user_details = Detail(user=user, college='Sta')
        user_details.save()

class DetailsForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    college = forms.ChoiceField(choices=(
            ('Chu', 'Churchill'),
            ('Cla', 'Clare'),
            ('ClH', 'Clare Hall'),
            ('Cor', 'Corpus Christi'),
            ('Dar', 'Darwin'),
            ('Dow', 'Downing'),
            ('Emm', 'Emmanuel'),
            ('Fit', 'Fitzwilliam'),
            ('Gir', 'Girton'),
            ('Gon', 'Gonville and Caius'),
            ('Hom', 'Homerton'),
            ('Hug', 'Hughes Hall'),
            ('Jes', 'Jesus'),
            ('Kin', 'King\'s'),
            ('Luc', 'Lucy Cavendish'),
            ('Mag', 'Magdalene'),
            ('Mur', 'Murray Edwards'),
            ('New', 'Newnham'),
            ('Pem', 'Pembroke'),
            ('Pet', 'Peterhouse'),
            ('Que', 'Queens\''),
            ('Rob', 'Robinson'),
            ('Sel', 'Selwyn'),
            ('Sid', 'Sidney Sussex'),
            ('SCa', 'St Catharine\'s'),
            ('SEd', 'St Edmund\'s'),
            ('SJo', 'St John\'s'),
            ('Tri', 'Trinity College'),
            ('TrH', 'Trinity Hall'),
            ('Wol', 'Wolfson'),
            ('Alu', 'Alumni'),
        ))

    def save(self, user):
        if not user.email:
            user.email = user.username + '@cam.ac.uk'

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user_details = getattr(user, 'detail', Detail(user=user))
        user_details.college = self.cleaned_data["college"]
        user.save()
        user_details.save()

class RequestForm(forms.Form):
    crsid = forms.CharField(max_length=10, required=False)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    diet = forms.CharField(max_length=200, required=False, label="Dietary requirements")
    access = forms.CharField(max_length=200, required=False, label="Accessibility requirements")

    def save(self, user):
        request = Request(
            user=user,
            date=timezone.now(),
            ticket_crsid=self.cleaned_data["crsid"],
            ticket_first_name=self.cleaned_data["first_name"],
            ticket_last_name=self.cleaned_data["last_name"],
            diet=self.cleaned_data["diet"],
            access=self.cleaned_data["access"],
        )

        ticket_count = Request.objects.filter(user=user).exclude(status='C').count()

        if user.detail.college == 'Chr':
            if ticket_count == 0:
                request.priority = 'CS'
            elif ticket_count == 1:
                request.priority = 'CF'
            elif ticket_count in (2,3):
                request.priority = 'CG'
            else:
                request.status = 'C'
        elif user.detail.college == 'Alu':
            request.priority = 'AL'
        elif user.detail.college == 'Sta':
            request.priority = 'ST'
            if Request.objects.filter(priority='ST').count() < constants.LIMIT_STAFF:
                request.status = 'H'
            else:
                request.status = 'P'
        else:
            request.priority = 'OC'

        if request.priority != 'ST':
            request.status = 'P'
        else:
            if Request.objects.filter(priority='ST').count() < constants.LIMIT_STAFF:
                request.status = 'H'
            else:
                request.status = 'P'

        if Request.objects.filter(ticket_first_name=self.cleaned_data["first_name"], ticket_last_name=self.cleaned_data["last_name"], user=user).exclude(status='C').exists():
            return

        request.save()

class NameForm(forms.Form):
    crsid = forms.CharField(max_length=10, required=False)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    diet = forms.CharField(max_length=200, required=False, label="Dietary requirements")
    access = forms.CharField(max_length=200, required=False, label="Accessibility requirements")

    def save(self, ticket_request):
        old_status = ticket_request.status
        ticket_request.status = 'C'
        ticket_request.save()
        ticket_request.status = old_status
        ticket_request.ticket_crsid = self.cleaned_data["crsid"]
        ticket_request.ticket_first_name = self.cleaned_data["first_name"]
        ticket_request.ticket_last_name = self.cleaned_data["last_name"]
        ticket_request.diet = self.cleaned_data["diet"]
        ticket_request.access = self.cleaned_data["access"]
        ticket_request.pk = None
        ticket_request.save()
