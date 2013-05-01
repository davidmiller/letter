"""
Fab commands for ffs
"""

from fabric.api import task, hosts, local, lcd,  cd, run
from fabric import operations

deadpan = 'happenup@deadpansincerity.com'

@task
def test():
    """
    Run our unittests
    """
    local('python -m pytest test')

@task
def make_docs():
    """
    Rebuild the documentation
    """
    with lcd('doc/'):
        local('make html')

@task
@hosts(deadpan)
def upload_docs():
    """
    Build, compress, upload and extract the latest docs
    """
    with lcd('doc/build/html'):
        local('rm -rf letterdocs.tar.gz')
        local('tar zcvf letterdocs.tar.gz *')
        operations.put('letterdocs.tar.gz', '/home/happenup/webapps/letterdocs/letterdocs.tar.gz')
    with cd('/home/happenup/webapps/letterdocs/'):
        run('tar zxvf letterdocs.tar.gz')
