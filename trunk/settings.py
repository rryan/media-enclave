## Template file for the Django settings for menclave project.
##
## Copy this file to settings.py, then customize it to fit your local
## installation. Comments beginning with "CUSTOMIZE ME" are mandatory
## customizations.
##
## DON'T RE-ADD SETTINGS.PY TO THE REPOSITORY!
## Not everybody has the same settings.

#================================= DEBUGGING =================================#

# Debug mode.  When enabled, makes pretty error pages and other useful things.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# If DEBUG is False, then any errors will be emailed to the ADMINS.
ADMINS = (('Media-Enclave Admins', 'media-enclave-admins@www.example.com'),)

# Information about broken links gets emailed to the MANAGERS.
SEND_BROKEN_LINK_EMAILS = False
MANAGERS = ADMINS

# Subject prefix for emails sent out to ADMINS or MANAGERS.
EMAIL_SUBJECT_PREFIX = '[Media-Enclave] '
SERVER_EMAIL="somebody@www.example.com"
DEFAULT_FROM_EMAIL="media-enclave@www.example.com"
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

# The login_required decorator uses this to determine where
# to redirect the user to login. It's lame to have this
# written here, though.
LOGIN_URL = "/audio/login"

# Turn on standard logging.
import logging
logging.basicConfig(level=logging.INFO)

#================================= SESSIONS ==================================#

SESSION_COOKIE_AGE = 60 * 60 * 24 * 3  # three days (in seconds)
SESSION_COOKIE_SECURE = False  # TODO change to True for deployment
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Don't leave cookies lying around.

#================================= DATABASE ==================================#

DATABASE_ENGINE = 'sqlite3'  # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
## CUSTOMIZE ME
DATABASE_NAME = '/home/skyewm/menclave/db'
  # Or path to database file if using sqlite3.
DATABASE_USER = ''      # Not used with sqlite3.
DATABASE_PASSWORD = ''  # Not used with sqlite3.
DATABASE_HOST = ''  # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''  # Set to empty string for default. Not used with sqlite3.

#=================================== MISC ====================================#

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

## CUSTOMIZE ME
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/path/to/media'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

### CUSTOMIZE ME
AENCLAVE_SFTP_UPLOAD_DIR = "/path/to/sftp-upload"

### CUSTOMIZE ME
AENCLAVE_DEQUEUE_NOISES_DIR = "/path/to/dequeue-noise"

### CUSTOMIZE ME
### At the moment, only "mp3" and "m4a"
SUPPORTED_AUDIO = ("mp3", "m4a")

# The host that the gst player will be running on.
GST_PLAYER_HOST = "localhost"

# The port that the gst player will be running on.
GST_PLAYER_PORT = 7890

# The authentication uses this user's perms as Anonymous
ANONYMOUS_USER = "ANONYMOUS_USER"

DEFAULT_GROUP = "Media-Enclave Users"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = "A LARGE STRING OF CHARACTERS AND NUMBERS. IF YOU DON'T CHANGE THIS YOU WILL BE HACKED"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#   'django.template.loaders.eggs.load_template_source',
)

# The only nonstandard template context processor is request.
TEMPLATE_CONTEXT_PROCESSORS = (
	"django.core.context_processors.request",
	"django.core.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'menclave.auth.KerberosBackend.KerberosBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'menclave.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.admin',  # gives us an admin site
    'django.contrib.auth',  # gives us users and groups
    'django.contrib.contenttypes',  # here by default; don't know what it's for
    'django.contrib.humanize',  # lets us use a few extra template filters
    'django.contrib.sessions',  # handles user logins
    #'media_bundler',  # bundles js and css
    # The below are the applications included in Media-Enclave.  Usually you
    # will pick one to leave uncommented.
    'menclave.aenclave',  # Audio Enclave
    'menclave.venclave',  # Video Enclave
    #'menclave.genclave',  # Gaming Enclave
)

# Enable these both to improve performance and hurt debugging.
DEFER_JAVASCRIPT = False
USE_BUNDLES = False

# CUSTOMIZE ME
_MENCLAVE_ROOT = "/path-to-menclave/"

# Bundles for media-enclave.
MEDIA_BUNDLES = (
    {"type": "javascript",
     "name": "aenclave-scripts",
     "path": _MENCLAVE_ROOT + "aenclave/scripts/",
     "url": "/audio/scripts/",
     "minify": True,
     "files": (
         "jquery-1.2.6.min.js",
         "jquery.clickmenu.js",
         "jquery.columnmanager.js",
         "jquery.cookie.min.js",
         "jquery.tablednd_0_5.js",
         "controls.js",
         "channels.js",
         "fancyupload.js",
         "fileprogress.js",
         "filter.js",
         "playlist.js",
         "songlist.js",
         "swfupload.js",
         "swfupload.cookies.js",
         "swfupload.queue.js",
         "tablesort.js",
         "upload.js",
     )},

    {"type": "css",
     "name": "aenclave-styles",
     "path": _MENCLAVE_ROOT + "/home/reid/menclave/aenclave/styles/",
     "url": "/audio/styles/",
     "minify": False,
     "files": (
         "base.css",
         "browse.css",
         "clickmenu.css",
         "filter.css",
         "login.css",
         "playlist.css",
         "sftp_info.css",
         "songlist.css",
         "upload.css",
     )},

    {"type": "png-sprite",
     "name": "aenclave-sprites",
     "path": _MENCLAVE_ROOT + "aenclave/images/",
     "url": "/audio/images/",
     "css_file": _MENCLAVE_ROOT + "/aenclave/styles/aenclave-sprites.css",
     "files": (
         "add.png",
         "cancel.png",
         "create.png",
         "cross.png",
         "delete.png",
         "dl.png",
         "edit.png",
         "email.png",
         "heart-gray.png",
         "heart-pink.png",
         "heart.png",
         "history.png",
         "maximize.png",
         "minimize.png",
         "new.png",
         "ok.png",
         "pause.png",
         "play.png",
         "remove.png",
         "selectcol.png",
         "shuffle.png",
         "skip.png",
         "sorta.png",
         "sortd.png",
         "speaker.png",
         "stop.png",
         "tick.png",
         "updown.png",
     )},
)

#=========================== DATE/TIME FORMATTING ============================#

# See all available format strings here:
# http://www.djangoproject.com/documentation/templates/#now

DATE_FORMAT = 'j M Y'             # 3 Dec 2006
DATETIME_FORMAT = 'j M Y H:i:s'   # 3 Dec 2006 15:34:12
TIME_FORMAT = 'H:i:s'             # 15:34:12
YEAR_MONTH_FORMAT = 'F Y'         # December 2006
MONTH_DAY_FORMAT = 'j F'          # 3 December

#=============================================================================#
