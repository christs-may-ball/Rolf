from django.db import models
from django.contrib.auth.models import User

class Detail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    charity = models.IntegerField(default=0)
    address = models.CharField(max_length=200, null=True, blank=True)
    college = models.CharField(max_length=3,
        choices=(
            ('Chr', 'Christ\'s'),
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
            ('Sta', 'Staff'),
        ))

    def __str__(self):
        return self.user.username + ': ' + str(self.balance) + ', ' + self.college + ', ' + (self.address or '')

class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    priority = models.CharField(max_length=2,
        choices=(
          ('CS', 'Christ\'s Student'),
          ('CF', 'Christ\'s First Guest'),
          ('CG', 'Christ\'s Other Guest'),
          ('OC', 'Other College'),
          ('AL', 'Alumni'),
          ('ST', 'Staff'),
        ))
    status = models.CharField(max_length=1,
        choices=(
            ('P', 'Pending'),
            ('H', 'Half'),
            ('C', 'Cancelled'),
            ('S', 'Standard'),
            ('Q', 'Queue Jump'),
            ('D', 'Dining'),
        ))
    ticket_crsid = models.CharField(max_length=10, null=True, blank=True)
    ticket_last_name = models.CharField(max_length=100)
    ticket_first_name = models.CharField(max_length=100)
    diet = models.CharField(max_length=200, null=True, blank=True)
    access = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.id) + ': ' + self.status + ', ' + self.priority + ', ' + self.date.strftime("%Y-%m-%d %H:%M:%S") + ', ' + self.ticket_first_name + ' ' + self.ticket_last_name + ', ' + self.ticket_crsid

class Alumni(models.Model):
    dob = models.DateField()
    matriculation_year = models.CharField(max_length=4, choices=[(str(year), str(year)) for year in range(1931, 2015)[::-1]])

    def __str__(self):
        return self.matriculation_year + ", " + str(self.dob)
