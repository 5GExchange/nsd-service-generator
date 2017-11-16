#### Usage
Create a dict in the python script according to the VNFDs to be included in the NSD. Please note that the VNFDs have to already be onboarded in the MarketPlace.
Please fill in the fields according to the information in each VNFD (i.e., domain, vnf_id and alias of the port):

```
vnfds_conf = [ {'domain': 'UCL', 'id' : '4', 'port' : '99'},
               {'domain': 'UCL', 'id' : '5', 'port' : '99'},
               {'domain': 'UCL', 'id' : '6', 'port' : '54'} ]
```

Fill in the information related to the ingress/egress points of the service according to the names of the SAPs you have previously created in the underlying infrastructure:

```
ingress = 'SAP0'
egress = 'SAP1'
```

Finally specify the total number of instances the NSD should include, the VNFs will be randomly added to the generated service descriptor according to the information of the previous dict.

```
nf_instances = 100
```
