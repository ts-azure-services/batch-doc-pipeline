"""One-time script to create a cluster"""
import os
from azure.ai.ml.entities import AmlCompute
from azure.ai.ml import MLClient
from azure.identity import EnvironmentCredential # DefaultAzureCredential
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv('./variables.env')

    cpu_compute_target = "cpu-cluster"

    ml_client = MLClient(credential=EnvironmentCredential(),
                     subscription_id=os.environ['SUB_ID'],
                     resource_group_name=os.environ['RESOURCE_GROUP'],
                     workspace_name=os.environ['WORKSPACE_NAME'],
                         )

    try:
        ml_client.compute.get(cpu_compute_target)
        print("Compute target already created.")
    except Exception:
        print("Creating a new cpu compute target...")
        compute = AmlCompute(name=cpu_compute_target,
                             size="STANDARD_DS3_V2",
                             min_instances=0,
                             max_instances=4)
        ml_client.compute.begin_create_or_update(compute)
