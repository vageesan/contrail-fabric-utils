from fabfile.config import *
from time import sleep

class OpenStackSetupError(Exception):
    pass

def verify_service(service):
    for x in xrange(10):
        output = run("service %s status" % service)
        keys_to_wait = ['STARTING', 'waiting', 'pre-start', 'post-start']
        if any(x in output for x in keys_to_wait):
            sleep(20)
        else:
            break
    if "running" not in output:
        if "RUNNING" not in output:
            raise SystemExit("Service %s not running." % service)
    
@task
@roles('database')
def verify_database():
    verify_service("supervisord-contrail-database")
    verify_service("contrail-database")

@task
@roles('webui')
def verify_webui():
    verify_service("supervisor-webui")
    #verify_service("contrail-webui-middleware")

@task
@roles('openstack')
def verify_openstack():
    if detect_ostype() in ['Ubuntu']:
        verify_service("keystone")
    else:
        verify_service("openstack-keystone")
    output = run("source /etc/contrail/openstackrc; keystone tenant-list")
    if 'error' in output:
        raise OpenStackSetupError(output)

@task
@roles('cfgm')
def verify_cfgm():
    verify_service("supervisor-config")
    verify_service("contrail-api")
    verify_service("contrail-discovery")
    verify_service("contrail-schema")
    verify_service("contrail-svc-monitor")
    #verify_service("contrail-zookeeper")
    #verify_service("ifmap")

@task
@roles('control')
def verify_control():
    verify_service("supervisor-control")
    verify_service("contrail-control")
    #verify_service("supervisor-dns")
    #verify_service("contrail-dns")
    #verify_service("contrail-named")

@task
@roles('collector')
def verify_collector():
    verify_service("supervisor-analytics")
    verify_service("contrail-collector")
    verify_service("contrail-opserver")
    verify_service("contrail-qe")
    verify_service("redis-query")
    #verify_service("redis-sentinel")
    verify_service("redis-uve")

@task
@roles('compute')
def verify_compute():
    verify_service("supervisor-vrouter")
    #verify_service("contrail-vrouter")


@task
@roles('compute')
def remove_startup_files():
    compute = env.host_string
    if compute not in env.roledefs['database']:
        run("rm /etc/init/supervisord-contrail-database.conf")
        run("rm /etc/contrail/supervisord_contrail_database.conf")
    if compute not in env.roledefs['collector']:
        run("rm /etc/init/supervisor-analytics.conf")
        run("rm /etc/contrail/supervisord_analytics.conf")
    if compute not in env.roledefs['webui']:
        run("rm /etc/init/supervisor-webui.conf")
        run("rm /etc/contrail/supervisord_webui.conf")
    if compute not in env.roledefs['cfgm']:
        run("rm /etc/init/supervisor-config.conf")
        run("rm /etc/contrail/supervisord_config.conf")
    if compute not in env.roledefs['control']:
        run("rm /etc/init/supervisor-dns.conf")
        run("rm /etc/init/supervisor-control.conf") 
        run("rm /etc/contrail/supervisord_dns.conf")
        run("rm /etc/contrail/supervisord_control.conf")
    if compute not in env.roledefs['compute']:
        run("rm /etc/init/supervisor-vrouter.conf")
        run("rm /etc/contrail/supervisord_vrouter.conf")

@task
@roles('compute')
def stop_glance_in_compute():
    compute = env.host_string
    if compute not in env.roledefs['cfgm']:
       run("service glance-api stop")
       run("service glance-registry stop")
