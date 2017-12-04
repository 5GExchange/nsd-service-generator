# Prometeus setup
Edit the `/etc/docker/daemon.json` to expose monitoring info:
```json
{
  "metrics-addr" : "127.0.0.1:9323",
  "experimental" : true
}
```
Inmediatelly after that restart the docker service:
```bash
service docker restart
```
In this setup I create a single node swarm with a manager node. The manager node is the machine you are using in this guide. So start a docker swarm using:
```bash
docker swarm init --advertise-addr <MANAGER-IP>
```
Now clone the prometeus repo:
```bash
git clone https://github.com/vegasbrianc/prometheus.git
```
and edit the `docker-compose.yml` file to specify that your machine will host the prometheus and alertmanager services:
```yaml
          # - node.hostname == moby
          - node.role == manager
```

Before deploying the stack (the docker-compose includes prometheus, cadvisor, node-exporter and graphana) make sure you are running docker 17.05 CE, otherwise you can retrieve this error:
```bash
1 error(s) decoding:

* invalid spec: /var/run:/var/run:rw: unknown option: rw
```

Once you've checked your docker version you can deploy the stack:
```bash
docker stack deploy -c docker-compose.yml prom
```
This will create all the services needed.
The next step is entering the graphana dashboard at `http://MANAGER-IP:3000`. Login using:
```txt
user: admin
password: foobar
```
Then 
 * Click the Grafana Menu at the top left corner (looks like a fireball)
 * Click Data Sources
 * Click the green button Add Data Source.
 * Set the URL to: `http://MANAGER-IP:9090`

Now that you've added the data-source, import the dashboard used to represent the stats at `Dashboard/import` and fill ID with `179`.


