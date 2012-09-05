"""
These are the django settings for the Seattle Clearinghouse project. See the README.txt
file for details on what needs to be set in this file. At a minimum for
development, it will be the database connection info and the SECRET_KEY value.

For public deployment, see the README.txt file for information about which
additional changes you'll need to make to this file.
"""

import os



from seattlegeni.common.util import log



# If DEBUG is True, then error details will be shown on the website and ADMINS
# will not receive an email when an error occurs. So, this should be False in
# production.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# The log level used by the seattlegeni log module. All messages at this level
# or more severe will be logged.
SEATTLECLEARINGHOUSE_LOG_LEVEL = log.LOG_LEVEL_DEBUG

# Rather than make the log module have to import this settings file to set the
# log level, just set it right here.
log.set_log_level(SEATTLECLEARINGHOUSE_LOG_LEVEL)

# This is needed to allow xmlrpc requests to work when they don't have a slash
# on the end of the url.
APPEND_SLASH = False

# The directory the settings.py file is in is what we consider the root of the website. 
SEATTLECLEARINGHOUSE_WEBSITE_ROOT = os.path.dirname(__file__)

# The directory where we keep the public keys of the node state keys.
SEATTLECLEARINGHOUSE_STATE_KEYS_DIR = os.path.join(SEATTLECLEARINGHOUSE_WEBSITE_ROOT, '..', 'node_state_transitions', 'statekeys')

# The XML-RPC interface to the Custom Installer Builder.
SEATTLECLEARINGHOUSE_INSTALLER_BUILDER_XMLRPC = "https://seattlegeni.cs.washington.edu/custom_install/xmlrpc/"

# The directory where the base installers named seattle_linux.tgz, seattle_mac.tgz,
# and seattle_win.zip are located.
SEATTLECLEARINGHOUSE_BASE_INSTALLERS_DIR = "/home/guypesto/trunk/dist/base_installers"

# The directory in which customized installers created by seattlegeni will be
# stored. A directory within this directory will be created for each user.
SEATTLECLEARINGHOUSE_USER_INSTALLERS_DIR = os.path.join(SEATTLECLEARINGHOUSE_BASE_INSTALLERS_DIR, "geni")

# The url that corresponds to SEATTLECLEARINGHOUSE_USER_INSTALLERS_DIR
SEATTLECLEARINGHOUSE_USER_INSTALLERS_URL = "https://blackbox.cs.washington.edu/dist/geni"

# Need to specify the LOGIN_URL, as our login page isn't at the default login
# location (the default is /accounts/login).
LOGIN_URL = 'login'
# This will allow pages that use the standard @login_required
# decorator to use the OpenID login page.
# Once a user is logged in, he gets redirected here.
#LOGIN_REDIRECT_URL = 'html/profile'
#LOGIN_REDIRECT_URL = 'done'

######################################
## Django social_auth URL Redirects ## 
######################################

# Users will be redirected to SOCIAL_AUTH_LOGIN_ERROR_URL in case of error/user cancellation
# during login or association (account linking).
SOCIAL_AUTH_LOGIN_ERROR_URL ='associate_error'

# If a OpenID/OAuth backend itself has an error(not a user or Seattle Clearinghouse's fault) 
# a user will get redirected here.
SOCIAL_AUTH_BACKEND_ERROR_URL = 'error'

#LOGIN_ERROR_URL='error2'

# When a logged in user removes a new OpenID/OAuth account ex google,yahoo.github etc he
# gets redirected to this page.  This should always be the profile page.  If not defined
# defaults to LOGIN_URL value

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'profile'

# The login page for OpenID/OAuth, Seattle Clearinghouse uses the same login page for
# regular login and OpenID/OAuth
SOCIAL_AUTH_LOGIN_URL = 'login'

# when a logged in user links a new OpenID/OAuth account ex google,yahoo.github etc he
# gets redirected to this page.  This should always be the profile page.
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = 'profile'
#TODO documentation
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email',]
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Email addresses of people that should be emailed when a 500 error occurs on
# the site when DEBUG = False (that is, in production). Leave this to be empty
# if nobody should receive an email. 
ADMINS = (
     ('Your Name', 'gppressi@gmail.com'),
)

# To be able to send mail to ADMINS when there is an error, django needs to
# know about an SMTP server it can use. That info is defined here.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'gppressi@gmail.com'
EMAIL_HOST_PASSWORD = '153Chatterton'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Email address that error notifications will be sent from.
SERVER_EMAIL = "error@seattlegeni.server.hostname"

# We use this so we know which server the email came from by the subject line.
EMAIL_SUBJECT_PREFIX = "[localhost] "

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'      # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'seattlegeni' # Or path to database file if using sqlite3.
DATABASE_USER = 'seattlegeni' # Not used with sqlite3.
DATABASE_PASSWORD = '' # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

if DATABASE_ENGINE == 'mysql':
  DATABASE_OPTIONS = {'init_command': 'SET storage_engine=INNODB'}

# Make this unique, and don't share it with anybody.
# Fill this in!
SECRET_KEY = ''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = SEATTLECLEARINGHOUSE_WEBSITE_ROOT + '/html/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.load_template_source',
  'django.template.loaders.app_directories.load_template_source',
# 'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.csrf.middleware.CsrfViewMiddleware',
  'django.contrib.csrf.middleware.CsrfResponseMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',	
  #'django.middleware.doc.XViewMiddleware',

  # Our own middleware that logs when a request is initially received and
  # sets up the logger to log other messages with per-request unique ids.
  'seattlegeni.website.middleware.logrequest.LogRequestMiddleware',
  # Our own middleware that logs when unhandled exceptions happen.
  'seattlegeni.website.middleware.logexception.LogExceptionMiddleware',
)

ROOT_URLCONF = 'seattlegeni.website.urls'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  SEATTLECLEARINGHOUSE_WEBSITE_ROOT + '/html/templates'
)


INSTALLED_APPS = (
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.csrf',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  # Needed for OpenID/OAuth login so must be listed. 
  'social_auth',

  # We have our maindb model defined here, so it must be listed.
  'seattlegeni.website.control',
)
  #####################
  ## OpenID & OAuth  ##
  #####################

  # Seattle Clearinghouse uses a django plugin called "django social auth" to handle
  # OpenID and OAuth.  The desired OpenID/OAuth providers must be listed here 
  # in order to be used.  Seattle Clearinghouse uses Facebook, Github, Windows Live
  # Google and Yahoo.       
  
AUTHENTICATION_BACKENDS = (
  
  'social_auth.backends.facebook.FacebookBackend',
  'social_auth.backends.google.GoogleBackend',
  'social_auth.backends.yahoo.YahooBackend',
  'social_auth.backends.contrib.github.GithubBackend',
  #'social_auth.backends.OpenIDBackend',  #needed???
  #'social_auth.backends.browserid.BrowserIDBackend',
  'social_auth.backends.contrib.live.LiveBackend',
  # Django default this is always needed and must always be last.
  'django.contrib.auth.backends.ModelBackend',	    
)
# Social_Auth needs OAuth keys in order to use.  Each backend provider has its
# own method to acquire keys.  Yahoo and Google are OpenID so we  
# dont need keys for them.

FACEBOOK_APP_ID                   = '154143918042976'
FACEBOOK_API_SECRET               = '32110dc11bd9ff27c1df614956757d8e'
LIVE_CLIENT_ID = '00000000440CAFB5'
LIVE_CLIENT_SECRET = '2hQOC1v9Co-ONCSwOhFBKaZYMeof2ka5'
#SOCIAL_AUTH_CREATE_USERS          = True
#SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
#SOCIAL_AUTH_DEFAULT_USERNAME      = 'socialauth_user'
SOCIAL_AUTH_ERROR_KEY             = 'socialauth_error'
GITHUB_APP_ID                     = 'b3923bd44ed078136488'
GITHUB_API_SECRET                 = '30ddef64dfef3c26a51d26e56602bf810ae6fe98'

FACEBOOK_EXTENDED_PERMISSIONS = ['email']

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',  
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'django.contrib.messages.context_processors.messages',
  # Adds a social_auth dict with keys: are associated, not_associated and backends. 
  # associated key is a list of UserSocialAuth instances associated with current user. 
  # not_associated is a list of providers names that the current user doesn't have any association yet. 
  # backends holds the list of backend names supported.  Each value is grouped by backend type openid, oauth2 and oauth.
  'social_auth.context_processors.social_auth_by_type_backends',
)
#TODO Social_auth follows each of these in order and passes along a object with
#     information gathered to each function.  
#     Custom fns can be written and passed in here we define them in seattlegeni.website.pipeline.
#     To use a custom fn you must call .save_status_to_session before your custom fn.
SOCIAL_AUTH_PIPELINE = (
  'seattlegeni.website.pipeline.custom_social_auth_user',
  #'social_auth.backends.pipeline.social.social_auth_user',
  'social_auth.backends.pipeline.associate.associate_by_email',
  #'social_auth.backends.pipeline.user.get_username',
  'social_auth.backends.pipeline.misc.save_status_to_session',
  'seattlegeni.website.pipeline.redirect_to_auto_register',
  'seattlegeni.website.pipeline.username',
  #'social_auth.backends.pipeline.misc.save_status_to_session',
  #'seattlegeni.website.pipeline.redirect_to_form2',
  #'seattlegeni.website.pipeline.custom_social_auth_user',
  'seattlegeni.website.pipeline.custom_create_user',
  #'social_auth.backends.pipeline.user.create_user',
  #'social_auth.backends.pipeline.user.get_username',
  'social_auth.backends.pipeline.social.associate_user',
  'social_auth.backends.pipeline.social.load_extra_data',
  'social_auth.backends.pipeline.user.update_user_details',
  #'social_auth.backends.pipeline.misc.save_status_to_session',
  #'seattlegeni.website.pipeline.redirect_to_form2',
  #'social_auth.backends.pipeline.user.update_user_details',
  #'social_auth.backends.pipeline.social.associate_user',
  #'social_auth.backends.pipeline.social.load_extra_data',
  #'seattlegeni.website.pipeline.first_name',
)

# default new user nickname if not provided  --------------------------------------------------------
# This is important for the partial pipeline, anytime it is broken with a custom
# function, it must be redirected back to SOCIAL_AUTH_COMPLETE_URL_NAME in order
# for the pipeline to continue.
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
#SOCIAL_AUTH_COMPLETE_URL_NAME  = 'done'
#SOCIAL_AUTH_PROCESS_EXCEPTIONS = 'social_auth.utils.process_exceptions'

# This should be false for production. Useful for debugging social_auth problems.
#SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_RAISE_EXCEPTIONS = True
#SOCIAL_AUTH_USER_MODEL = 'control.GeniUser'
SOCIAL_AUTH_LAST_LOGIN = 'social_auth_last_login_backend'
SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
#SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
# Backends will store extra values from response by default, set this to False to avoid such behavior:
# SOCIAL_AUTH_EXTRA_DATA = False
#----------------------------------------------------------------------------------------------------
# The number of seconds sessions are valid for. Django uses this for the
# session expiration in the database in addition to the cookie expiration,
# which is good.
SESSION_COOKIE_AGE = 3600

# Use session cookies, not persistent cookies.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
