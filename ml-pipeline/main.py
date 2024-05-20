import os
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import MLClient, dsl, Input, Output
from azure.ai.ml.parallel import parallel_run_function, RunFunction
from azure.identity import ClientSecretCredential, EnvironmentCredential
from dotenv import load_dotenv

load_dotenv('./variables.env')

# ml_client = MLClient(credential=EnvironmentCredential(),
#                      subscription_id=os.environ['SUB_ID'],
#                      resource_group_name=os.environ['RESOURCE_GROUP'],
#                      workspace_name=os.environ['WORKSPACE_NAME'],
#                      )

tenant_id = os.environ["AZURE_TENANT_ID"]
client_id = os.environ["AZURE_CLIENT_ID"]
client_secret = os.environ["AZURE_CLIENT_SECRET"]

ml_client = MLClient(credential=ClientSecretCredential(tenant_id, client_id, client_secret),
                     subscription_id=os.environ['SUB_ID'],
                     resource_group_name=os.environ['RESOURCE_GROUP'],
                     workspace_name=os.environ['WORKSPACE_NAME'],
                     )
# Paths for output to be persisted
pdf_file_inputs="wasbs://perkins16blobcontainer@perkins1storage5f763e753.blob.core.windows.net/perkins16blobcontainer/"
# text_file_outputs="wasbs://perkins2235blobcontainer@perkins2storagef8d0e420d.blob.core.windows.net/outputs/"
text_file_outputs="azureml://datastores/workspaceblobstore/paths/parallel-pipeline-ocr-outputs/"

# Convert images to text
pdf_convert_component = parallel_run_function(
    name="convert_images_to_txt",
    display_name="Convert PDF docs to text",
    description="Convert PDF documents to text files",
    inputs=dict(job_data_path=Input(type=AssetTypes.URI_FOLDER,)),
    input_data="${{inputs.job_data_path}}",
    outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER)),# path=blob_store_path)),
    instance_count=4,
    max_concurrency_per_instance=2,
    mini_batch_size="1",
    mini_batch_error_threshold=1,
    retry_settings=dict(max_retries=2, timeout=60),
    logging_level="DEBUG",
    task=RunFunction(
        code="./",
        entry_script="./scripts/png_to_ocr_entry.py",
        program_arguments="--job_output_path ${{outputs.job_output_path}}",
        environment="read-docs:1",
    ),
)

@dsl.pipeline(compute='cpu-cluster')
def par_pipeline(pdf_inputs):
    pdf_conversion = pdf_convert_component(job_data_path=pdf_inputs)
    return {"pdf_job_output": pdf_conversion.outputs.job_output_path,
            }

# INSTANTIATE THE PIPELINE
pipeline = par_pipeline(pdf_inputs=Input(type=AssetTypes.URI_FOLDER, path=pdf_file_inputs),)
pipeline.outputs.pdf_job_output = Output(type=AssetTypes.URI_FOLDER, path=text_file_outputs)

# SUBMIT THE PIPELINE JOB
pipeline_job = ml_client.jobs.create_or_update(pipeline, experiment_name="pdf-docs-to-text",)
