__author__ = 'wbert'

# What do I need to do to initial deploy?
# pip install all python libs
# set up postgres database
# git archive, then unpack and install source
# restart apache

# Update deploy
# on dev:
# git push origin master  (puts it on webfaction /git repo)
#
# on prod:
# pull from origin
# possibly run python manage.py collectstatic
# possibly run syncdb
# possibly do south migration
# apache2/bin/restart

# import fabrics API functions - self-explanatory once you see
from fabric.api import *

PROD_HOST = 'wjb@wjb.webfactional.com:22'
PROD_DIR = '/home/wjb/webapps/doreadme/doreadme'
PROD_ACTIVATE = '/home/wjb/.virtualenvs/doreadme/bin/activate'

def prod():
    """Set up the environment for the current production server."""
    env['hosts'] = [PROD_HOST]
    env['dir'] = PROD_DIR
    env.activate = PROD_ACTIVATE

def push():
    """On local, push latest commit to master to origin."""
    local('git push origin master') # runs the command on the local environment

def pull():
    """On prod, pull the latest from origin/master."""
    with cd(env['dir']):
        run('git pull origin master') # runs the command on the remote environment

def restart_apache():
    """Restart apache"""
    with cd(env['dir']):
        run('../apache2/bin/restart')

def virtualenv(command):
    with cd(env.dir):
        run(env.activate + '&&' + command)

def collectstatic():
    """Run manage.py collectstatic, suppressing any input."""
    with cd(env['dir']):
        virtualenv('python manage.py collectstatic')
    restart_apache()

def migrate(*args):
    """South migrations"""
    with cd(env['dir']):
        virtualenv('python manage.py migrate ' + " ".join(args))

def pip_install():
    """Install from pip requirements"""
    virtualenv('pip install -r ../requirements.txt')

def revert():
    """ Revert git via reset --hard @{1} """
    with cd(env['dir']):
        run('git reset --hard @{1}')
        restart_apache()

def restart_supervisor():
    with cd(env['dir']):
        virtualenv('python manage.py supervisor --daemonize') # This should only run if supervisor is not already running
        virtualenv('python manage.py restart celeryd')
        virtualenv('python manage.py restart celerybeat')

def deploy():
    """Deploy to prod. Calls prod(), push(), pull(), restart_apache()"""
    # TODO figure out how to specify whether to collectstatic and migrate.
    print "Env hosts: %s" % env.hosts
    push()
    pull()
    pip_install()
    migrate()
    # if something, then collectstatic()
    restart_supervisor()
    restart_apache()
