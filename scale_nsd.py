#!/usr/bin/python

import json
import random


def generate_vnffgd(ingress, egress, vnfds, nfs_number):
    vnffgd = {}

    vnffgd['vnffgs']=[]
    vnffgs = {}
    vnffgs['vnffg_id'] = "vnffg0"
    vnffgs['number_of_endpoints'] = nfs_number
    vnffgs['number_of_virtual_links'] = nfs_number+1
    vnffgs['dependent_virtual_links'] = []

    for i in xrange(nfs_number+1):    
          vnffgs['dependent_virtual_links'].append('vld'+str(i))

    network_forwarding_path = {}
    network_forwarding_path['nfp_id'] = 'nfp0'
    network_forwarding_path['graph'] = vnffgs['dependent_virtual_links']

    network_forwarding_path['connection_points'] = []
    network_forwarding_path['connection_points'].append('ns_ext_' + ingress)

    vnfd_index = random.randint(0, len(vnfds)-1)
    vnfd = vnfds[vnfd_index]

    network_forwarding_path['connection_points'].append(vnfd['vnfid'] + '-' + str(vnfd['instances']) + ':ext_' + str(vnfd['port']))

    for i in xrange(nfs_number-1):
          # using previous instance and port
          network_forwarding_path['connection_points'].append(vnfd['vnfid'] + '-' + str(vnfd['instances']) + ':ext_' + str(vnfd['port']))
          # incrementing the instance id
          vnfds[vnfd_index]['instances']+=1
          # picking a new VNFD
          vnfd_index = random.randint(0, len(vnfds)-1)
          vnfd = vnfds[vnfd_index]
          network_forwarding_path['connection_points'].append(vnfd['vnfid'] + '-' + str(vnfd['instances']) + ':ext_' + str(vnfd['port']))

    network_forwarding_path['connection_points'].append('ns_ext_' + egress)
    network_forwarding_path['connection_points'].append(vnfd['vnfid'] + '-' + str(vnfd['instances']) + ':ext_' + str(vnfd['port']))
    vnfds[vnfd_index]['instances']+=1
    
    constituent_vnfs = []

    for vnfd in vnfds:
        domain = vnfd['vnfid'].split(':')[0].split('#')[1]
        vnf_id = vnfd['vnfid'].split(':')[1].split('#')[1]

        for instance in xrange(vnfd['instances']):    
            vnf = {'vnf_ref_id' : str(vnf_id) + '@' + domain + '-' + str(instance),
                   'vnf_flavor_key_ref': 'gold'}
            constituent_vnfs.append(vnf)

    network_forwarding_path['constituent_vnfs'] = constituent_vnfs

    vnffgs['network_forwarding_path']=[]
    vnffgs['network_forwarding_path'].append(network_forwarding_path)

    vnffgd['vnffgs'].append(vnffgs)

    return vnffgd



def generate_vlds(vnffg, ingress, egress):
    vld = {}
    vld['number_of_endpoints'] = 0

    virtual_links = []
    
    vl_ids = vnffg['network_forwarding_path'][0]['graph']
    conn_points = vnffg['network_forwarding_path'][0]['connection_points']

    for i, vl_id in enumerate(vl_ids):
          vl = {}
          vl['vld_id'] = vl_id
          if i==0:
             vl['alias'] = ingress
             vl['external_access'] = True
             connections = [conn_points[1]]
          elif i==len(vl_ids)-1:
             vl['alias'] = egress
             vl['external_access'] = True
             connections = [conn_points[len(conn_points)-1]]
          else:
             vl['alias'] = 'internal'
             vl['external_access'] = False
             connections = [conn_points[(i*2)], conn_points[(i*2)+1]]
         
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

    vld['virtual_links'] = virtual_links

    return vld

                                                                                                                        
def generate_sla(vnfds):

    constituent_vnf = []
    for vnfd in vnfds:
        domain = vnfd['vnfid'].split(':')[0].split('#')[1]
        vnf_id = vnfd['vnfid'].split(':')[1].split('#')[1]
        vnf_info = {}
        vnf_info['number_of_instances'] = vnfd['instances']
        vnf_info['redundancy_model'] = 'Active'
        vnf_info['vnf_flavour_id_reference'] = 'gold'
        vnf_info['vnf_reference'] = vnf_id + '@' + domain
        constituent_vnf.append(vnf_info)

    sla = [ {'id': 'sla0',
             'assurance_parameters': [],
             'billing': {'model': 'PAYG',
                         'price': {'price_per_period': 1,
                                   'setup': 1,
                                   'unit': 'EUR'
                                  }
                        },
             'constituent_vnf' : constituent_vnf,
             'sla_key' : 'basic' 
             } ]

    return sla


def generate_nsd(ns_id, ns_name, vnfds, vnf_number, ingress, egress):
    nsd = {
           'id' : ns_id,
           'name' : ns_name,
           'vendor' : "3",
           'version' : "1",
           'vnfds' : [vnfd['vnfid'] for vnfd in vnfds],
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
    
    vnffgd = generate_vnffgd(ingress, egress, vnfds, vnf_number)
    nsd['vnffgd'] = vnffgd

    vld = generate_vlds(vnffgd['vnffgs'][0], ingress, egress)

    nsd['vld'] = vld

    sla = generate_sla(vnfds)
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

   #vnfds_conf = [ {'domain': 'UCL', 'id' : '4', 'port' : '99'},
   #               {'domain': 'UCL', 'id' : '5', 'port' : '99'},
   #               {'domain': 'UCL', 'id' : '6', 'port' : '54'} ]

   vnfds_conf = [ {'domain': 'UCL', 'id' : '4', 'port' : '99'},
                  {'domain': 'UCL', 'id' : '5', 'port' : '99'} ]

   ingress = 'SAP0'
   egress = 'SAP1'
   nf_instances = 9

   vnfds = []
   for vnfd in vnfds_conf:
       vnfds.append({'vnfid' : 'domain#'+ vnfd['domain'] + ':vnf#' + vnfd['id'], 'port' : vnfd['port'], 'instances' : 0})
   
   generate_nsd('myID', 'myName', vnfds, nf_instances, ingress + ':in', egress + ':out')
