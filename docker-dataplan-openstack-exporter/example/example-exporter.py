from prometheus_client import CollectorRegistry, generate_latest, Gauge, CONTENT_TYPE_LATEST
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ForkingMixIn
import urlparse
import traceback

class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    pass

class OpenstackExporterHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        url = urlparse.urlparse(self.path)
        if url.path == '/metrics':
            try:
                registry = CollectorRegistry()
                labels = ['cloud', 'subnet_name', 'tenant', 'ip_type', 'ip_status']
                metrics = Gauge('neutron_public_ip_usage',
                        'Neutron floating IP and router IP usage statistics',
                        labels, registry=registry)
                print "Label : %s" % labels
        	    print "registry %s" % registry
                k = { 'cloud':"banana", 'subnet_name':"banana_subnet", 'tenant':"banana", 'ip_type':"floatingIP", 'ip_status':"ACTIVE" }
                print "Key : %s " % type(k)
		        v = 3
                metrics.labels(*k).set(v)
		
		        print "traceback.format_exc(): %s" % traceback.format_exc()
                print "---------"
        
                output =  generate_latest(registry)
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
    OpenstackExporterHandler(*args, **kwargs)



if __name__ == '__main__':
    # Start up the server to expose the metrics.
    # start_http_server(8000)
    port=9999
    addr='0.0.0.0'
    server = ForkingHTTPServer((addr,port), handler)
    server.serve_forever()

