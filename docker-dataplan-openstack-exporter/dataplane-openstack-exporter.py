import os
from keystoneauth1.identity import v3 as keystone_v3
from keystoneauth1 import session as keystone_session
from keystoneclient.v3 import client as keystone_client
from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client
from cinderclient import client as cinder_client
from prometheus_client import CollectorRegistry, generate_latest, Gauge, CONTENT_TYPE_LATEST
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer as http_server
from SocketServer import ForkingMixIn as forking_mix_in
import urlparse
import traceback

def getParaauthen(*parameters_authen): 
    list_value_authen = dict([ (parameter_authen , os.getenv("OS_%s" % parameter_authen.upper())) for parameter_authen in parameters_authen ])
    return list_value_authen

def authenOpenstack(**kwargs):
    authen = keystone_v3.Password(**kwargs)
    session = keystone_session.Session(auth=authen)
    keystone = keystone_client.Client(session=session)
    neutron = neutron_client.Client(session=session, endpoint_type="internalURL")
    nova = nova_client.Client(2,session=session, endpoint_type="internalURL")
    cinder = cinder_client.Client(2,session=session, endpoint_type="internalURL")
    return (keystone,nova,neutron,cinder) 
    
class exporterCinder:
    def __init__(self,cinder):
        self.cinder = cinder
        self.data_cinder_service_alive = {}
        self.labels_cinder = ['cloud' , 'region' , 'service' , 'host' , 'zone' ]
        self.cloud_name = "ols-huawei"
        self.region_name = os.getenv("OS_REGION_NAME")
        self.registry = CollectorRegistry()    

    def getCinderservice(self):
        list_cinder_services = self.cinder.services.list()     
        for cinder_service in list_cinder_services:
            key_label_cinder_service = ( str(self.cloud_name) , str(self.region_name) ,  str(cinder_service.binary) ,str(cinder_service.host)  ,str(cinder_service.zone) )
            value_cinder_alive  = int( cinder_service.state == "up" )
            print ("cinder State : %s " % cinder_service.state)
            self.data_cinder_service_alive[key_label_cinder_service] = value_cinder_alive
            
    def getStat(self):
        labels = self.labels_cinder
        metrics = Gauge('openstack_services_cinder_total',
                        'Cinder service alive',
                        self.labels_cinder, registry=self.registry)
        for key_cinder_serivce_alive, value_cinder_serivce_alive in self.data_cinder_service_alive.items():
            metrics.labels(*key_cinder_serivce_alive).set(value_cinder_serivce_alive)

        output_cinder_service_alive = generate_latest(self.registry)
        return output_cinder_service_alive

class exporterNova:
    def __init__(self,nova):
        self.nova = nova
        self.data_nova_service_alive = {}
        self.labels_nova = ['cloud' , 'region' , 'service' , 'host' , 'id' , 'zone' ]
        self.cloud_name = "ols-huawei"
        self.region_name = os.getenv("OS_REGION_NAME")
        self.registry = CollectorRegistry()    

    def getNovaservice(self):
        list_nova_services = self.nova.services.list()     
        for nova_service in list_nova_services:
            key_label_nova_service = ( str(self.cloud_name) , str(self.region_name) ,  str(nova_service.binary) ,str(nova_service.host) , str(nova_service.id) , str(nova_service.zone) )
            value_nova_alive  = int( nova_service.state == "up" )
            print ("Nova State : %s " % nova_service.state)
            self.data_nova_service_alive[key_label_nova_service] = value_nova_alive       

    def getStat(self):
        labels = self.labels_nova
        metrics = Gauge('openstack_services_nova_total',
                        'Nova service alive',
                        self.labels_nova, registry=self.registry)
        for key_nova_serivce_alive, value_nova_serivce_alive in self.data_nova_service_alive.items():
            metrics.labels(*key_nova_serivce_alive).set(value_nova_serivce_alive)

        output_nova_service_alive = generate_latest(self.registry)
        return output_nova_service_alive

class exporterNeutron:
    def __init__(self,neutron):
        self.neutron = neutron
        self.data_neutron_service_alive = {}
        self.labels_neutron = ['cloud' , 'region' , 'service' , 'host' , 'id' ]
        self.cloud_name = "ols-huawei"
        self.region_name = os.getenv("OS_REGION_NAME")
        self.registry = CollectorRegistry()    

    def getNeutronservice(self):
        list_neutron_services = self.neutron.list_agents()["agents"]        
        for neutron_service in list_neutron_services:
            key_label_neutron_service = ( str(self.cloud_name) , str(self.region_name) ,  str(neutron_service["binary"]) ,str(neutron_service["host"]) ,str(neutron_service["id"]) )
            value_neutron_alive  = int( neutron_service["alive"] == True )
            self.data_neutron_service_alive[key_label_neutron_service] = value_neutron_alive
            

    def getStat(self):
        labels = self.labels_neutron
        metrics = Gauge('openstack_services_neutron_total',
                        'Neutron service alive',
                        self.labels_neutron, registry=self.registry)
        for key_neutron_serivce_alive, value_neutron_serivce_alive in self.data_neutron_service_alive.items():
            metrics.labels(*key_neutron_serivce_alive).set(value_neutron_serivce_alive)

        output_neutron_service_alive = generate_latest(self.registry)
        return output_neutron_service_alive

class forkingHTTPserver(forking_mix_in, http_server):
    pass

class openstackExporterhandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        url = urlparse.urlparse(self.path)
        if url.path == '/metrics':
            try:
                authen_keystone,authen_nova,authen_neutron,authen_cinder = authenOpenstack(**getParaauthen("username","password", "user_domain_name", "auth_url","project_domain_name", "project_name"))
                neutron = exporterNeutron(authen_neutron)
                neutron.getNeutronservice()
                cinder = exporterCinder(authen_cinder)
                cinder.getCinderservice()
                nova = exporterNova(authen_nova)
                nova.getNovaservice()
                output =  nova.getStat()  + cinder.getStat() + neutron.getStat()

                self.send_response(200)
                self.send_header('Content-Type', CONTENT_TYPE_LATEST)
                self.end_headers()
                self.wfile.write(output)
            except:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(traceback.format_exc())
        elif url.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write("""<html>
            <head><title>OpenStack Exporter</title></head>
            <body>
            <h1>OpenStack Exporter</h1>
            <p>Visit <code>/metrics</code> to use.</p>
            </body>
            </html>""")
        else:
            self.send_response(404)
            self.end_headers()

def handler(*args, **kwargs):
    openstackExporterhandler(*args, **kwargs)


if __name__ == '__main__':
    port=9999
    addr='0.0.0.0'
    server = forkingHTTPserver((addr,port), handler)
    server.serve_forever()


