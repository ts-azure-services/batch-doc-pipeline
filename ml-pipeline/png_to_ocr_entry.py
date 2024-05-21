"""Script to create images from PDF files"""
import os
import argparse
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


def init():
    global OUTPUT_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_output_path", type=str, default=0)
    args, _ = parser.parse_known_args()
    OUTPUT_PATH = args.job_output_path

    global document_analysis_client
    document_analysis_client = DocumentAnalysisClient(
            endpoint='https://westus.api.cognitive.microsoft.com/',
            credential=AzureKeyCredential('<input key>'),
    )
    print("Pass through init done.")


def run(mini_batch):
    # mini_batch is a list of file paths for File Data
    for file_path in mini_batch:
        print(f'Processing: {file_path}')
        get_ocr_from_image(file_path)
    return mini_batch


# Get form recognizer output
def analyze_read(client, image_file):
    """Get form recognizer analysis"""
    with open(image_file, 'rb') as filename:
        poller = client.begin_analyze_document("prebuilt-read", document=filename, locale='en-US')
    result = poller.result()
    return result.content


# Write out and save results to a file
def write_out_output(result, output_path, filename):
    with open(output_path + '/' + filename, 'w') as f:
        f.write(result)


def get_ocr_from_image(file_path):
    # Create the output path for the recognizer output
    image_filename = file_path.split('/')[-2:][1]
    image_filename = image_filename.replace('pdf', 'txt')

    # Create outputPath with the directory
    outputPath = OUTPUT_PATH + '/'
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    result = analyze_read(client=document_analysis_client, image_file=file_path)
    write_out_output(result=result, output_path=outputPath, filename=image_filename)
