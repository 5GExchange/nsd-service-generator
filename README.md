#### Usage
Create a dict in the python script according to the VNFDs to be referenced in the NSD. Please note that the VNFDs have to already be onboarded in the MarketPlace.
Please fill in the fields according to the information related to each VNFD (i.e., domain, vnf_id and identifier [alias] of the port):

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

Specify the total number of VNFs the NSD should include, the instances will randomly be referenced in the generated service descriptor according to the information of the previous dict.

```
nf_instances = 30
```

Finally assign the name of the NSD file (it will also used as value of the name field in the descriptor itself)

```
service_name = '30Instances_NSD'
```

#### Service submission
To actually submit the generated NSD to the 5GEx marketplace and purchase an instance of it, please use the script

```
# submit_service.sh <MdO IP> <NSD.json> <Service name in the NSD>
```
