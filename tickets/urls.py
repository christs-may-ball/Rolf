from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/details/$', views.details, name='details'),
    url(r'^alumni/register/$', views.register, name='register'),
    url(r'^alumni/success/$', views.success, name='success'),
    url(r'^alumni/failure/$', views.failure, name='failure'),
    url(r'^alumni/login/$', views.login, name='login'),
    url(r'^staff/register/$', views.register_staff, name='register_staff'),
    url(r'^staff/login/$', views.login, name='login_staff'),
    url(r'^admin/login/$', views.admin_redirect),
    url(r'^tickets/request/$', views.request, name='request'),
    url(r'^tickets/queue/(?P<pk>[0-9]+)/$', views.queue, name='queue'),
    url(r'^tickets/dining/(?P<pk>[0-9]+)/$', views.dining, name='dining'),
    url(r'^tickets/charity/$', views.charity, name='charity'),
    url(r'^tickets/standard/(?P<pk>[0-9]+)/$', views.standard, name='standard'),
    # url(r'^tickets/name/(?P<pk>[0-9]+)/$', views.name, name='name'),
    # url(r'^tickets/namepay/(?P<pk>[0-9]+)/$', views.namepay, name='namepay'),
    url(r'^tickets/confirm/(?P<confirmation>[a-z\/]+)/(?P<pk>[0-9]+)/$', views.confirm, name='confirm'),
    url(r'^tickets/pay/', views.pay, name='pay'),
    url(r'^tickets/payment_error/', views.payment_error, name='payment_error'),
]
