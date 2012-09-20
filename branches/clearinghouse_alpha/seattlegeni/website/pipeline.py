"""
Custom pipeline functions used in Seattle Clearinghouse.

"""
from django.http import HttpResponseRedirect
from social_auth.backends.exceptions import AuthException
from social_auth.backends.pipeline.social import social_auth_user
from seattlegeni.website.control import interface
from seattlegeni.website.control import models
from uuid import uuid4

from social_auth.utils import setting
from social_auth.models import User
from social_auth.backends.pipeline import USERNAME, USERNAME_MAX_LENGTH, \
                                          warn_setting
from social_auth.signals import socialauth_not_registered, \
                                socialauth_registered, \
                                pre_update
                                
def redirect_to_auto_register(*args, **kwargs):
    if not kwargs['request'].session.get('saved_username') and \
       kwargs.get('user') is None:
        return HttpResponseRedirect('/html/auto_register')


def username(request, *args, **kwargs):
    if kwargs.get('user'):
        username = kwargs['user'].username
    else:
        username = request.session.get('saved_username')
    return {'username': username}

#NOT USED
#def redirect_to_form2(*args, **kwargs):
#    ''' NOT USED '''
#    if not kwargs['request'].session.get('saved_first_name'):
#        return HttpResponseRedirect('/social_register/')


#def first_name(request, *args, **kwargs):
#    if 'saved_first_name' in request.session:
#        user = kwargs['user']
#        user.first_name = request.session.get('saved_first_name')
#        user.save()
        
def custom_social_auth_user(*args, **kwargs):
    try:
        return social_auth_user(*args, **kwargs)
    except AuthException:# Raise AuthException if UserSocialAuth entry belongs to another user.:
    	 return HttpResponseRedirect('html/associate_error')
    #except UserSocialAuth.DoesNotExist:	 
    #	 return HttpResponseRedirect('social_register')              
    
#def custom_create_user(*args, **kwargs):
def custom_create_user(backend, details, response, uid, username, user=None, *args,
                **kwargs):
    """Create user. Depends on get_username pipeline."""
    if user:
        return {'user': user}
    if not username:
        return None
    
    warn_setting('SOCIAL_AUTH_CREATE_USERS', 'create_user')
  
    if not setting('SOCIAL_AUTH_CREATE_USERS', True):
        # Send signal for cases where tracking failed registering is useful.
        socialauth_not_registered.send(sender=backend.__class__,
                                       uid=uid,
                                       response=response,
                                       details=details)
        return None
    #set a random password 10 characters long
    #password=models.UserManager.make_random_password(10)    
    #email = details.get('email')
    #affiliation= 'auto-register@'+ details.get('backend') 
    #backend = kwargs['backend']  / backend = request.session[name]['backend']
    # or just use backend=backend cuz of parameter autoregister-Facebook
    #user = interface.register_user(username, password, email, affiliation)
    user = interface.register_user(username, password='123456', email=details.get('email'), affiliation='auto-register@'+ backend.name)
    return {
        'user': user,
        'is_new': True
    }             
