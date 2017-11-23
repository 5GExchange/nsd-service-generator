#!/bin/sh -e

#based on single domain vCDN test on the CI

if [ "$#" -ne 2 ] ; then
	echo "Missing parameters: "
	echo "Usage $0 [MDO_IP] [Service name in the NSD]"
	exit 1
fi


MDO_IP=$1

echo "login to marketplace as Customer"
TOKEN_CUSTOMER=`curl -s -X POST -H 'Content-Type: application/json;charset=UTF-8'  -d '{"username":"customer1","password":"123456"}' http://$MDO_IP/auth/ | jq -r '.token'`

sleep 1

echo "...Getting the service id"
SERVICE_ID=`curl -s -H "Content-Type: application/json" -H "Authorization:JWT $TOKEN_CUSTOMER"  http://$MDO_IP/service-catalog/service/catalog/ | jq -r ".[]| select(.nsd.name==\"$2\") | {id: .nsd.id}" | jq -r '.id'`

if [ -z "$SERVICE_ID" ] ; then
	echo "Missing service id. Test failed"
	exit 1
fi
echo "Got service id: $SERVICE_ID"

sleep 2

echo "...Purchasing service as Customer1"
INPUT=`jq ".ns_id = \"$SERVICE_ID\"" service_purchase.json`
RESP=`curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "Authorization:JWT $TOKEN_CUSTOMER" -d "$INPUT" http://$MDO_IP/service-selection/service/selection/`

echo "Response: $RESP"

if [ "$RESP" -ne 200 ] &&  [ "$RESP" -ne 201 ] ; then
	echo "Response != 200. Something wrong happened"
else 
	echo "...Service purchased. Test OK"	
fi
