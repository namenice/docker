Prometheus Openstack Exporter
============

## Pre-requisites
```
Config File sample-openrc
make
docker  
```

## Quick Start

Deploy 
```
make deploy-dataplan
```

Destroy
```
make destroy-dataplan
```
Image for a prometheus exporter for openstack API derived metrics.

## Environment

check sample env file provided in the source.

* OS_USERNAME
  - username associated with the monitoring project that project's role is admin in openstack , used for polling openstack API, **required**

* OS_PASSWORD
  - password for the username associated with the monitoring project that project's role is admin in openstack, used for polling openstack API, **required**

* OS_USER_DOMAIN_NAME 
  - user's domain name associated with the monitoring project that project's role is admin in openstack, used for polling openstack API, **required**

* OS_PROJECT_DOMAIN_NAME 
  - project's domain name associated with the monitoring project that project's role is admin in openstack, used for polling openstack API, **required**

* OS_PROJECT_NAME
  - monitoring tenant/project that project's role is admin in openstack, used for polling openstack API, **required**

* OS_AUTH_URL
  - openstack keystone API endpoint for only keystone version 3, **required**

* OS_REGION_NAME
  - openstack region to use keystone service catalog against **required**


## Docker Usage
docker build -t dataplane-openstack-exporter .

docker run -d --env-file sample-openrc -p 9000:9999 **\<docker-image-id\>**

## sample test
curl http://localhost:9000/metrics
```
# HELP openstack_services_neutron_total Neutron service alive
# TYPE openstack_services_neutron_total gauge
openstack_services_neutron_total{cloud="mycloud",host="network2",id="d1541364-623f-4c77-abebc9b28bc7",region="regionone",service="neutron-metering-agent"} 1.0
openstack_services_neutron_total{cloud="mycloud",host="compute1",id="ae24fbb9-0c5f-4175-50424a78cfa8",region="regionone",service="neutron-metadata-agent"} 1.0
openstack_services_neutron_total{cloud="mycloud",host="network2",id="d25385db-5ea1-4eee-97270e9a61e6",region="regionone",service="neutron-lbaasv2-agent"} 0.0
```

