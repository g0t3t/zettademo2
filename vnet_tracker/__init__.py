import logging
import os
import json
import traceback
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.cosmos import CosmosClient
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Read environment variables
        subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
        cosmos_endpoint = os.environ['COSMOS_ENDPOINT']
        cosmos_key = os.environ['COSMOS_KEY']

        # Authenticate
        credential = DefaultAzureCredential()
        network_client = NetworkManagementClient(credential, subscription_id)

        # Get all VNETs
        vnets = list(network_client.virtual_networks.list_all())

        # Prepare VNET data
        vnet_data = []
        for vnet in vnets:
            subnets = []
            if vnet.subnets:
                for subnet in vnet.subnets:
                    subnets.append({
                        'name': subnet.name,
                        'address_prefix': subnet.address_prefix,
                        'id': subnet.id
                    })

            vnet_info = {
                'id': f"{vnet.id.split('/')[4]}-{vnet.name}",
                'resource_id': vnet.id,
                'name': vnet.name,
                'location': vnet.location,
                'address_space': vnet.address_space.address_prefixes,
                'subnets': subnets,
                'resource_group': vnet.id.split('/')[4]
            }
            vnet_data.append(vnet_info)

        # Store in Cosmos DB
        cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = cosmos_client.get_database_client('vnetdb')
        container = database.get_container_client('vnetdata')

        for item in vnet_data:
            container.upsert_item(item)

        return func.HttpResponse(
            json.dumps({"status": "success", "data": vnet_data}, indent=2),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Unhandled exception: {str(e)}\n{error_trace}")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": str(e),
                "trace": error_trace
            }),
            status_code=500,
            mimetype="application/json"
        )
