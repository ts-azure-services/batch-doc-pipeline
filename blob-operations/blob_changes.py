import os
import argparse
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

def get_data_files(start_path="./pdf-files"):
    """Get all generated data files"""
    filepath_list = []
    for root, _ , files in os.walk(start_path):
        for file in files:
            filepath_list.append(os.path.join(root, file))
    return filepath_list


def list_files(blob_service_client: BlobServiceClient, container_name: str):
    """List contents of existing container"""
    file_list = []
    container_client = blob_service_client.get_container_client(container=container_name)
    for blob in container_client.list_blobs():
        file_list.append(blob.name)
    return file_list


def delete_blob_files(blob_service_client: BlobServiceClient, container_name: str):
    """Delete existing files"""
    container_client = blob_service_client.get_container_client(container=container_name)
    for blob in container_client.list_blobs():
        container_client.delete_blob(blob.name)


def delete_specific_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name:str):
    """Delete specific blob"""
    container_client = blob_service_client.get_container_client(container=container_name)
    container_client.delete_blob(blob_name)



def upload_blob_file(blob_service_client: BlobServiceClient, container_name: str, local_file_path: str):
    """Upload blob files"""
    container_client = blob_service_client.get_container_client(container=container_name)
    blob_name = local_file_path.split('/')[-1]
    with open(file=local_file_path, mode="rb") as data:
        # blob_client = container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="Blob container for source pdf files",required=True, type=str)
    parser.add_argument("-d", "--destination", help="Destination container with text files", required=True, type=str)
    parser.add_argument("-l", "--list_blob", action='store_true', help="List blobs")
    parser.add_argument("-dl", "--delete_blob", action='store_true', help="Delete blob")
    parser.add_argument("-ds", action='store_true', help="Delete source blob")
    parser.add_argument("-dd", action='store_true', help="Delete destination blob")
    parser.add_argument("--compare", action='store_true', help="Compare common files between blobs")
    parser.add_argument("-dsf", action='store_true', help="Delete specific file")
    args = parser.parse_args()

    load_dotenv('./variables.env')
    connection_string = os.environ["STORAGE_CONN_STRING"]
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Delete blobs within specified container
    if args.ds:
        delete_blob_files(blob_service_client, args.source)
        print("Deleted all files in the source container..")

    if args.dd:
        delete_blob_files(blob_service_client, args.destination)
        print("Deleted all files in the destination container..")

    # List files for all containers
    if args.list_blob:
        source_blob_files = list_files(blob_service_client, container_name=args.source)
        for file in source_blob_files:
            print(file)
        print(f"Source container files: {len(source_blob_files)}")
              
        destination_blob_files = list_files(blob_service_client, container_name=args.destination)
        for file in destination_blob_files:
            print(file)
        print(f"Destination container files: {len(destination_blob_files)}")

    # Compare files from both containers
    if args.compare:
        source_blob_files = list_files(blob_service_client, container_name=args.source)
        destination_blob_files = list_files(blob_service_client, container_name=args.destination)
        source_blob_files = [x.split('.')[0] for x in source_blob_files]
        destination_blob_files = [x.split('.')[0] for x in destination_blob_files]

        common_elements = list(set(source_blob_files).intersection(set(destination_blob_files)))
        print(f"Common files between both blobs: {len(common_elements)}")
        for file in common_elements:
            print(file)

        # Delete common files if argument flagged
        if args.dsf:
            for file in common_elements:
                source_format = str(file) + '.pdf'
                destination_format = str(file) + '.txt'
                try:
                    delete_specific_blob(blob_service_client, args.source, blob_name=source_format)
                    delete_specific_blob(blob_service_client, args.destination, blob_name=destination_format)
                    print(f"Successfully deleted source file: {source_format} and destination file: {destination_format} files.")
                except Exception as err:
                    print(err)
