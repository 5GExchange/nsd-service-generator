# Use nsd-scale along mock_do and mdoP2.0.3
## Environment
We'll use 2 machines here:
 * VM1: IP1
 * VM2: IP2
 
we deploy the P2.0.3-mock_do in VM1, and mock_do in VM2.

## Setup
### mock_do setup
First of all, you need to run the mock_do on your VM2.
Clone the repo:
```bash
git clone git@5gexgit.tmit.bme.hu:tusa/mock-orchestrator.git
cd mock-orchestrator
git submodule init
git submodule update
```
and build the docker image to run the mock_do as a container:
```bash
sudo docker build --no-cache --rm -t mock_do .
docker run -d -p 8889:8889 --name my_mock_do mock_do
```

### Escape setup and NSD test
Log in VM1 and checkout to P2.0.3:
```bash
git clone git@5gexgit.tmit.bme.hu:5gex/mdo.git
cd mdo
git checkout P2.0.3-mock_do
```
change your `.env` file to point P2.0.3 versions:
```bash
# Default image versions for mdo components
MARKETPLACE_VERSION=P2.0.3-mock_do
TNOVA_CONNECTOR_VERSION=P2.0.3-mock_do
ESCAPE_VERSION=P2.0.3-mock_do
TADS_VERSION=P2.0.3-mock_do
IMOS_VERSION=P2.0.3-mock_do
# Secret key for Django apps
SECRET_KEY=^9xi7kyli7-43r(m5b5ykl5uq@61kuk-4zyd$c2q-o&ma&gllo
# URL of the Docker Registry to use for VNF images
REGISTRY_HOST=https://5gex.tmit.bme.hu
# The name of the Docker Registry service as used in authentication calls
REGISTRY_SERVICE=registry.5gex
# Docker Registry user and password for the Marketplace (no defaults)
MARKETPLACE_REGISTRY_USER=fgxdev
MARKETPLACE_REGISTRY_PASSWORD=5GEXhack3r29
DOMAIN_ID=02
MDO_HOST=http://IP1
```
where `IP1` is the IP address of VM1 (the one we are working on to deploy the MdO).
Next step is to configure the ESCAPE configuration file. Inside the MdO's directory run:
```bash
cp -R sample-config/exp-vcdn-multi-mdo/config-mdo-master/ config
```
and create the ESCAPE configuration file `config/escape/mdo.config` to look like this:
```json
{
    "service": {
        "MAPPER": {
            "mapping-enabled": false
        }
    },
    "orchestration": {
        "Sl-Or": {
            "virtualizer_type": "GLOBAL"
        }
    },
    "adaptation": {
        "CALLBACK": {
            "timeout": 1000
        },
        "CLEAR-DOMAINS-AFTER-SHUTDOWN": true,
        "MANAGERS": [
            "Docker1"
        ],
        "Docker1": {
            "module": "escape.adapt.managers",
            "class": "UnifyDomainManager",
            "domain_name": "Docker1",
            "diff": true,
            "poll": false,
            "adapters": {
                "REMOTE": {
                    "timeout": 10,
                    "module": "escape.adapt.adapters",
                    "class": "UnifyRESTAdapter",
                    "prefix": "ro/infra",
                    "url": "http://IP2:8889"
                },
                "CALLBACK": {
                    "enabled": true,
                    "explicit_host": "IP1",
                    "explicit_update": true
                }
            }
        }
    }
}

```

your `docker-compose.yml` file must be changed in the escape entry to look like this:
```yaml
  escape:
    image: 5gex.tmit.bme.hu/escape:${ESCAPE_VERSION:-latest}
    volumes:
    - ./config/escape/mdo.config:/opt/escape/mdo.config:ro
    ports:
    # ESCAPE basic interfaces for requesting topology and deploying services
    - 8008:8008
    - 8888:8888
    # Debug interface for the internal topology
    - 8889:8889
    # Dedicated interface for callback coming from configured domains
    - 9000:9000
    command: --debug --rosapi --bypassapi --config mdo.config
    logging:
      options:
        max-size: "1M"
```

Next step is the creation of the proper NSD and VNF for the experiment
First of all, clone the repo:
```bash
git clone git@5gexgit.tmit.bme.hu:tusa/nsd-scaling.git
```

and modify the VNFD JSON files (`fake_cache_vnfd.json` and `fake_firewall_vnfd.json`) to set their `domain` value to the `DOMAIN_ID` specified in the MdO `.env` file (in this example it is `"02"`).
Set the `'domain'` value in the dictionaries contained in the `vnfds_conf` variable of file `scale_nsd.py` to the `DOMAIN_ID` value as well, and modify it to create a 10 instances NSD:
```python
   vnfds_conf = [ {'domain': '02', 'id' : '4', 'port' : '99'},
                  {'domain': '02', 'id' : '5', 'port' : '99'} ]

   ingress = 'SAP0'
   egress = 'SAP1'
   nf_instances = 10
   service_name = '10Instances_NSD'
```

Now create the NSD using:
```bash
python scale_nsd.py
```
Copy the VNFD JSON files to the directory `marketplace` inside the Mdo repo, i.e.:
```text
mdo
|--marketplace/
   |-fake_cache_vnfd.json
   |-fake_firewall_vnfd.json
```
Now move to the mdo repo and now run `./deploy.sh -i` to create the images (use `-u` in case you need to update the container versions).

Finally go back to the nsd-scaling repo and execute the test:
```bash
./create_service.sh IP1 10Instances_NSD.json
./instantiate_service.sh IP1 10Instances_NSD
```
changing `IP1` to be the IP address of VM1.






