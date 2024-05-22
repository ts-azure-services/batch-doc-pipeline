import os
import argparse
from azure.ai.ml.entities import AzureBlobDatastore
from azure.ai.ml.entities import AccountKeyConfiguration
from dotenv import load_dotenv
from azure.ai.ml import MLClient
from azure.identity import EnvironmentCredential

if __name__ == "__main__":
    load_dotenv('./variables.env')

    ml_client = MLClient(credential=EnvironmentCredential(),
                     subscription_id=os.environ['SUB_ID'],
                     resource_group_name=os.environ['RESOURCE_GROUP'],
                     workspace_name=os.environ['WORKSPACE_NAME'],
                         )
    parser = argparse.ArgumentParser()
    parser.add_argument("--container_name", type=str)
    parser.add_argument("--datastore_name", type=str)
    parser.add_argument("--datastore_desc", type=str)
    args = parser.parse_args()

    try:
        store = AzureBlobDatastore(
            name=args.datastore_name,
            description=args.datastore_desc,
            account_name=os.environ['STORAGE_ACCOUNT'],
            container_name=args.container_name,
            protocol="https",
            credentials=AccountKeyConfiguration(account_key=os.environ['STORAGE_ACCOUNT_KEY']),
        )

        ml_client.create_or_update(store)
    except Exception as e:
        print(f"Error: {e}")
