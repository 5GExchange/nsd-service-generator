# Use nsd-scale along mock_do and mdoP2.0.3
## Environment
We'll use 2 machines here:
 * VM1: IP1
 * VM2: IP2
 
we deploy the mdoP2.0.3 in VM1, and mock_do in VM2.

## Setup
### mock_do setup
First of all, you need to run the mock_do on your VM2.
Clone the repo:
```bash
git clone git@5gexgit.tmit.bme.hu:tusa/mock-orchestrator.git
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
git checkout P2.0.3
```
change your `.env` file to point P2.0.3 versions:
```bash
# Default image versions for mdo components
MARKETPLACE_VERSION=P2.0.3
TNOVA_CONNECTOR_VERSION=P2.0.3
ESCAPE_VERSION=P2.0.3
TADS_VERSION=P2.0.3
IMOS_VERSION=P2.0.3
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
MDO_HOST=IP1
```
where `IP1` is the IP address of VM1 (the one we are working on to deploy the MdO).
Next step is to configure the ESCAPE configuration file. Inside the MdO's directory run:
```bash
cp -R sample-config/exp-vcdn-multi-mdo/config-mdo-master/ config
```
and edit the ESCAPE configuration file "adapters" value to look like this:
```json
"adapters": {
    "REMOTE": {
        "timeout": 2,
        "module": "escape.adapt.adapters",
        "class": "UnifyRESTAdapter",
        "prefix": "ro/infra",
        "url": "http://IP2:8889"
    },
    "CALLBACK": {
        "enabled": true,
        "address": "0.0.0.0",
        "port": 9001,
        "timeout": 20,
        "callback_url": "http://IP1:9001/callback",
        "explicit_update": true
    }
}
```
and now run `./deploy.sh -i` to create the images. Once the marketplace is
deployed, we need to upload the VNFs of the NDS scaling test.
First of all, clone the repo:
```bash
git clone git@5gexgit.tmit.bme.hu:tusa/nsd-scaling.git
```

and modify the VNFD JSON files (`fake_cache_vnfd.json` and `fake_firewall_vnfd.json`) to set their `domain` value to the `DOMAIN_ID` specified in the MdO `.env` file (in this example it is `"02"`).
Set the `'domain'` value in the dictionaries contained in the `vnfds_conf` variable of file `scale_nsd.py` to the `DOMAIN_ID` value as well. 

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
Now move to the mdo repo and upload the VNFs to the marketplace:

```bash
sudo docker-compose -f docker-compose.yml -f docker-compose.admin.yml run --rm marketplace-cli
```

Finally go back to the nsd-scaling repo and execute the test:
```bash
./create_service.sh IP1 30Instances_NSD.json
./instantiate_service.sh IP1 30Instances_NSD
```
changing `IP1` to be the IP address of VM1.






