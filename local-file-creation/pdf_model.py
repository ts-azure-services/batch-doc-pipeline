"""Goal is to use the pre-built read model to get text from a PDF document"""
import os
import argparse
# from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv


# formatting function
def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in polygon])

def analyze_read(data_file, output_path):
    # sample form document
    load_dotenv('./variables.env')
    print(os.environ["COG_KEY"])
    document_analysis_client = DocumentIntelligenceClient(endpoint=os.environ['ENDPOINT'],
                                                      credential=AzureKeyCredential(os.environ['COG_KEY']))

    # Read sample data from PDF
    with open(data_file, 'rb') as f:
        poller = document_analysis_client.begin_analyze_document("prebuilt-read", analyze_request=f,
                                                                 content_type="application/octet-stream")
    result = poller.result()

    # Write full text out to text file
    with open(output_path, 'w') as f:
        f.write(result.content)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_input_file", help="PDF document to input")
    parser.add_argument("-o", "--output_path", help="Path to store OCR results")
    args = parser.parse_args()

    analyze_read(data_file=args.data_input_file, output_path=args.output_path)
