# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get('ENV') == 'PRODUCTION':
    DEBUG = False
else:
    DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY', 'c@n%u@91tum=@j392g20b8znh7dqfo-v%81))gxbbmu$=dy_*)') # development key for the moment

ALLOWED_HOSTS = ['baptiste-foodapp.herokuapp.com']

if os.environ.get('ENV') == 'PRODUCTION':
    
    # Static files settings
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

    # Extra places for collectstatic to find static files.
    STATICFILES_DIRS = (
        os.path.join(PROJECT_ROOT, 'static'),
    )