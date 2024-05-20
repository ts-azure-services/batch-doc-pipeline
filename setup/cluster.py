# Script to setup cluster in AML
import os
# from azure.core.credentials import AzureKeyCredential
from azure.identity import EnvironmentCredential # DefaultAzureCredential
from azure.ai.ml.entities import AmlCompute
from azure.ai.ml import MLClient
from dotenv import load_dotenv

load_dotenv('./variables.env')

ml_client = MLClient(credential=EnvironmentCredential(),
                     subscription_id=os.environ['SUB_ID'],
                     resource_group_name=os.environ['RESOURCE_GROUP'],
                     workspace_name=os.environ['WORKSPACE_NAME'],)
# Specify aml compute name.
cpu_compute_target = "cpu-cluster"

try:
    ml_client.compute.get(cpu_compute_target)
    print("Compute target already created.")
except Exception:
    print("Creating a new cpu compute target...")
    compute = AmlCompute(name=cpu_compute_target,
                         size="STANDARD_D2_V2",
                         min_instances=1,
                         max_instances=4)
    ml_client.compute.begin_create_or_update(compute)
