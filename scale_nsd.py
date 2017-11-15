#!/usr/bin/python

import json


def generate_vnffgd(ingress, egress, vnf_port, nfs_number, domain, provider_id):
    vnffgd = {}

    vnffgd['vnffgs']=[]
    vnffgs = {}
    vnffgs['vnffg_id'] = "vnffg0"
    vnffgs['number_of_endpoints'] = nfs_number
    vnffgs['number_of_virtual_links'] = nfs_number+1
    vnffgs['dependent_virtual_links'] = []

    i=0
    while i<=nfs_number:
          vnffgs['dependent_virtual_links'].append('vld'+str(i))
          i+=1

    network_forwarding_path = {}
    network_forwarding_path['nfp_id'] = 'nfp0'
    network_forwarding_path['graph'] = vnffgs['dependent_virtual_links']

    network_forwarding_path['connection_points'] = []
    network_forwarding_path['connection_points'].append('ns_ext_' + ingress)

    vnfds = 'domain#' + domain + ':vnf#' + str(provider_id)
    network_forwarding_path['connection_points'].append(vnfds + '-' + str(0) + ':ext_' + str(vnf_port))

    i=0
    while i<nfs_number-1:
          network_forwarding_path['connection_points'].append(vnfds + '-' + str(i) + ':ext_' + str(vnf_port))
          network_forwarding_path['connection_points'].append(vnfds + '-' + str(i+1) + ':ext_' + str(vnf_port))
          i+=1
         
    network_forwarding_path['connection_points'].append('ns_ext_' + egress)
    network_forwarding_path['connection_points'].append(vnfds + '-' + str(nfs_number-1) + ':ext_' + str(vnf_port))     

    constituent_vnfs = []
    i=0
    while i<nfs_number:
          vnf = {'vnf_ref_id' : str(provider_id) + '@' + domain + '-' + str(i),
                 'vnf_flavor_key_ref': 'gold'}
          constituent_vnfs.append(vnf)
          i+=1

    network_forwarding_path['constituent_vnfs'] = constituent_vnfs

    vnffgs['network_forwarding_path']=[]
    vnffgs['network_forwarding_path'].append(network_forwarding_path)

    vnffgd['vnffgs'].append(vnffgs)

    return vnffgd



def generate_vlds(ingress, egress, vnf_port, nfs_number, domain, provider_id):
    vld = {}
    vld['number_of_endpoints'] = 0

    i=0
    virtual_links = []
    
    while i<=nfs_number:
          vl = {}
          vl['vld_id'] = 'vld' + str(i)
          if i==0:
             vl['alias'] = ingress
             vl['external_access'] = True
             connections = ['domain#' + domain + ':vnf#' + str(provider_id) + '-' + str(i) + ':ext_' + vnf_port]
          elif i==nfs_number:
             vl['alias'] = egress
             vl['external_access'] = True
             connections = ['domain#' + domain + ':vnf#' + str(provider_id) + '-' + str(i-1) + ':ext_' + vnf_port]
          else:
             vl['alias'] = 'internal'
             vl['external_access'] = False
             connections = ['domain#' + domain + ':vnf#' + str(provider_id) + '-' + str(i-1) + ':ext_' + vnf_port,
                            'domain#' + domain + ':vnf#' + str(provider_id) + '-' + str(i) + ':ext_' + vnf_port]
          
          vl['connections'] = connections   
          vl['root_requirements'] =  '10Mbps'
          vl['leaf_requirement'] = '10Mbps'

          qos = {}
          qos['peak'] = ''
          qos['burst'] = ''
          qos['delay'] = ''
          qos['flowclass'] = ''
          qos['params'] = ''
         
          vl['qos'] = qos
          vl['connectivity_type'] = 'E-LINE'
          vl['merge'] = False
          vl['sla_ref_id'] = 'sla0'

          virtual_links.append(vl)
          i+=1

    vld['virtual_links'] = virtual_links

    return vld

                                                                                                                        
def generate_sla(nfs_number, domain, provider_id):
    sla = [ {'id': 'sla0',
             'assurance_parameters': [],
             'billing': {'model': 'PAYG',
                         'price': {'price_per_period': 1,
                                   'setup': 1,
                                   'unit': 'EUR'
                                  }
                        },
             'constituent_vnf' : [ {'number_of_instances' : nfs_number,
                                    'redundancy_model' : 'Active',
                                    'vnf_flavour_id_reference': 'gold',
                                    'vnf_reference' : str(provider_id) + '@' + domain
                                   } ], 
             'sla_key' : 'basic' 
             } ]

    return sla


def generate_nsd(ns_id, ns_name, vnfds, vnf_number, domain, provider_id, ingress, egress, vnf_port):
    nsd = {
           'id' : ns_id,
           'name' : ns_name,
           'vendor' : "3",
           'version' : "1",
           'vnfds' : vnfds,
           'lifecycle_events' : {
                                 'start' : [],
                                 'stop' : [],
                                 'scale_out' : [],
                                 'scale_in' : []
                                },
    
           'monitoring_parameters' : [ {'desc' : 'Memory consumed',
                                        'metric': 'mem_used',
                                        'unit': 'Bytes'},
                                        
                                       {'desc': 'Memory consumed',
                                        'metric': 'mem_percent',
                                        'unit': '%'},

                                       {'desc': 'CPU',
                                        'metric': 'cpu_percent',
                                        'unit': '%'},

                                       {'desc': 'Bytes transmitted',
                                        'metric': 'tx_bytes',
                                        'unit': 'Bytes'},

                                       {'desc': 'Bytes received',
                                        'metric': 'rx_bytes',
                                        'unit': 'Bytes'} ],

           'vld' : {},
           'vnf_dependency' : []
          }
    
    vnffgd = generate_vnffgd(ingress, egress, vnf_port, vnf_number, domain, provider_id)
    nsd['vnffgd'] = vnffgd

    vld = generate_vlds(ingress, egress, vnf_port, vnf_number, domain, provider_id)
    nsd['vld'] = vld

    sla = generate_sla(vnf_number, domain, provider_id)
    nsd['sla'] = sla

    nsd['auto_scale_policy'] = {'criteria': [],
                                'basic' : [] }
    nsd['connection_points'] = []
    nsd['provider'] = '5GEx'
    nsd['description'] = 'test NSD'
    nsd['provider_id'] = '3'
    nsd['descriptor_version'] = '1'

    descriptor = {}
    descriptor['nsd'] = nsd

    print json.dumps(descriptor, sort_keys=True, indent=4) 
   


if __name__ == '__main__':

   domain = 'UCL'
   provider_id = '4'
   ingress = 'SAP0:in'
   egress = 'SAP1:out'
   vnf_port_id = '99'
   nf_instances = 100

   vnfds = ['domain#'+ domain + ':vnf#' + provider_id]
   generate_nsd('myID', 'myName', vnfds, nf_instances, domain, provider_id, ingress, egress, vnf_port_id)
