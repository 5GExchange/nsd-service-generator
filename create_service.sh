#!/bin/sh -e

#based on single domain vCDN test on the CI

if [ "$#" -ne 3 ] ; then
	echo "Missing parameters: "
	echo "Usage $0 [MDO_IP] [NSD file]"
	exit 1
fi


MDO_IP=$1

echo "login to marketplace as Service Provider"
TOKEN=`curl -s -X POST -H "Content-Type: application/json" -d '{"username":"sp1","password":"123456"}' http://$MDO_IP/auth/ | jq -r '.token'`

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ] ; then
	echo "Error: login failed"
	exit 1
fi
echo "Login as sp1 successful. Token: $TOKEN"

sleep 1

echo "Creating service $2"
RESP=`curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "Authorization:JWT $TOKEN" -d @$2 http://$MDO_IP/service-catalog/service/catalog/`

echo "Response: $RESP"
if [ "$RESP" -ne 200 ] &&  [ "$RESP" -ne 201 ] ; then
	echo "Error in creating service: $RESP"
	exit 1
fi
