import argparse
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import dsl, Input, Output
from azure.ai.ml.parallel import parallel_run_function, RunFunction
import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from common.authenticate import ml_client

# # Paths for output to be persisted
# blob_store_path="azureml://datastores/workspaceblobstore/paths/parallel-pipeline-pdf-images/"
# ocr_store_path="azureml://datastores/workspaceblobstore/paths/parallel-pipeline-ocr-outputs/"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_datastore", type=str)
    parser.add_argument("--intermediate_datastore", type=str)
    parser.add_argument("--output_datastore", type=str)
    args = parser.parse_args()

    # Convert PDFs to text
    ocr_convert_component = parallel_run_function(
        name="convert_pdf_to_text",
        display_name="Convert PDF documents to text files",
        description="Convert PDF documents to text files",
        inputs=dict(job_data_path=Input(type=AssetTypes.URI_FOLDER,)),
        input_data="${{inputs.job_data_path}}",
        outputs=dict(job_output_path=Output(type=AssetTypes.URI_FOLDER)),
        instance_count=4,
        max_concurrency_per_instance=2,
        mini_batch_size="1",
        mini_batch_error_threshold=1,
        retry_settings=dict(max_retries=2, timeout=60),
        logging_level="DEBUG",
        task=RunFunction(
            code="./",
            entry_script="./ml-pipeline/png_to_ocr_entry.py",
            program_arguments="--job_output_path ${{outputs.job_output_path}}",
            environment="form-rec-env:1",
        ),
        is_deterministic=False,
    )

    # DEFINE THE PIPELINE
    @dsl.pipeline(compute='cpu-cluster',)
    def par_pipeline(pdf_inputs):
        ocr_conversion = ocr_convert_component(job_data_path=pdf_inputs)
        return {"ocr_job_output": ocr_conversion.outputs.job_output_path}

    # INSTANTIATE THE PIPELINE
    pipeline = par_pipeline(pdf_inputs=Input(type=AssetTypes.URI_FOLDER, path=args.input_datastore),)
    pipeline.outputs.ocr_job_output = Output(type=AssetTypes.URI_FOLDER, path=args.output_datastore)

    # SUBMIT THE PIPELINE JOB
    pipeline_job = ml_client.jobs.create_or_update(pipeline, experiment_name="pipeline-parallel",)
