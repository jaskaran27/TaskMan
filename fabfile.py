from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

#env.users = ['ec2-user']
#env.hosts = ['ec2-54-255-94-63.ap-southeast-1.compute.amazonaws.com', 'ec2-54-255-122-34.ap-southeast-1.compute.amazonaws.com']

def test():
    with settings(warn_only=True):
        result = local('python ./manage.py test taskmanager', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -A && git commit", capture=False)

def push():
    local("git push origin master")

def prepare_deploy():
    test()
    commit()
    push()

def deploy():
    code_dir = '/coding/django/TaskMan'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone user@vcshost:/path/to/repo/.git %s" % code_dir)
    with cd(code_dir):
        run("git pull")
        run("touch app.wsgi")
