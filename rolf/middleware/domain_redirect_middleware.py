import datetime

from django.http import HttpResponseRedirect
from django.utils import timezone

class DomainRedirectMiddleware(object):
    def process_request(self, request):
        if timezone.now() < datetime.datetime(2016, 1, 22, 12, 0, 0, 0, tzinfo=datetime.timezone.utc) and not ('admin' in request.path or 'login' in request.path or 'raven_return' in request.path):
            return HttpResponseRedirect('http://christsmayball.com/ticketing.html')
        if not request.META['HTTP_HOST'].endswith('herokuapp.com'):
            return HttpResponseRedirect('https://christs.herokuapp.com%s' % request.path)