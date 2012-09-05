from django.conf.urls.defaults import *

from django.conf import settings
from django.views.generic.simple import redirect_to
from django.views.generic import RedirectView
from django.shortcuts import render_to_response, redirect
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#from seattlegeni.website.html.views import done, logout, error, form, form2, social_register, associate_error
from seattlegeni.website.html.views import error, associate_error, profile
admin.autodiscover()

# We override the default error handler because we want to pass a RequestContext
# to the template so that it can know the MEDIA_URL and so look nice.
handler500 = 'seattlegeni.website.html.errorviews.internal_error'

urlpatterns = patterns('',
    
    (r'^html/', include('seattlegeni.website.html.urls')),
    (r'^download/', include('seattlegeni.website.html.downloadurls')),
    (r'^xmlrpc', include('seattlegeni.website.xmlrpc.urls')),
    (r'^reports/', include('seattlegeni.website.reports.urls')),
    #OPENID django social auth
    #(r'^complete/google/', redirect_to, {'url': 'error'}),
    #(r'^complete/google/$', include('seattlegeni.website.html.urls')),
    
    #url(r'^form/$', form, name='form'),
    #url(r'^form2/$', form2, name='form2'),
    #url(r'^logout/$', logout, name='logout'),
    #url(r'^social_register/$', social_register, name='social_register'),
    ##url(r'^done$', done, name='done'),
    url(r'^complete/(?P<backend>[^/]+)/error', RedirectView.as_view(url='/html/error')), #wrong doesnt send backend as parameter
    url(r'^complete/(?P<backend>[^/]+)/associate_error', RedirectView.as_view(url='/html/associate_error')),
    #url(r'^complete/(?P<backend>[^/]+)/login', RedirectView.as_view(url='/html/login')),
    #url(r'^complete/(?P<backend>[^/]+)/profile', profile, name='profile'),
    url(r'^complete/(?P<backend>[^/]+)/profile', RedirectView.as_view(url='/html/profile')),
    #url(r'^complete/(?P<backend>[^/]+)/social_register', social_register, name='social_register'),
    url(r'^disconnect/(?P<backend>[^/]+)/profile', RedirectView.as_view(url='/html/profile')),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/profile',profile, name='profile'),
    (r'', include('social_auth.urls')),
    
   # (r'^login/$', redirect_to, {'url': '/login/github'}),
   # (r'^private/$', 'home.views.private'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

#urlpatterns += patterns('seattlegeni.website.html.views',
#     url(r'^form/$', form, name='form'),
#    url(r'^form2/$', form2, name='form2'),
#    url(r'^logout/$', logout, name='logout'),
#    (r'', include('social_auth.urls')),)
   
# If DEBUG is True, then this is for development rather than production. So,
# have django serve static files so apache isn't needed for development.
if settings.DEBUG:
  urlpatterns += patterns('',
      (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
  )
