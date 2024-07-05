# ifndef VERBOSE
# .SILENT:
# endif

venv-setup:
	rm -rf .venv
	python3.9 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r ./requirements.txt

sub-init:
	echo "SUB_ID=<enter subscription name>" > sub.env


# Infrastructure setup
infra:
	./setup/create-resources.sh

create-cluster:
	.venv/bin/python ./setup/aml-setup/cluster.py

create-env:
	.venv/bin/python ./setup/aml-setup/env.py --name "form-rec-env" \
		--conda_file "./setup/aml-env-config/form-rec-env.yml"

# create-kv:
# 	.venv/bin/python ./setup/aml-setup/create-kv.py

pdf_blob=$(shell cat variables.env | grep "BLOB_CONTAINER_PDF" | cut -d "=" -f 2 | xargs)
text_blob=$(shell cat variables.env | grep "BLOB_CONTAINER_TXT" | cut -d "=" -f 2 | xargs)
create-datastores:
	.venv/bin/python ./setup/aml-setup/datastore.py --container_name $(pdf_blob) \
		--datastore_name "pdfinputfiles" \
		--datastore_desc "PDF input files"
	.venv/bin/python ./setup/aml-setup/datastore.py --container_name $(text_blob) \
		--datastore_name "textfiles" \
		--datastore_desc "Final text files"

# For a sample PDF, refer the azure-ai-studio documentation; this should be a +700 page pdf
## If running in the cloud shell, upload the azure-ai-studio pdf
# Then, use the script below to generate several PDFs out of this base PDF and upload to blob
input_file="./azure-ai-studio.pdf"
number_of_pdfs=10
create-pdfs:
	rm -rf ./pdf-files
	mkdir -p ./pdf-files
	.venv/bin/python ./setup/pdf-creation/create_pdfs.py --input_file=$(input_file) --number_of_pdfs=$(number_of_pdfs)

upload-files:
	.venv/bin/python ./setup/pdf-creation/upload_data.py


# Substitute the <enter api key> with the right COG KEY
# Assumes sed available on Linux/Unix distribution
cog_key=$(shell cat variables.env | grep "COG_KEY" | cut -d "=" -f 2 | xargs)
sub-api-key:
	sed -i 's/<enter api key>/$(cog_key)/g' ./ml-pipeline/main.py


# Run ML pipeline
primary_datastore="azureml://datastores/pdfinputfiles/paths/"
output_datastore="azureml://datastores/textfiles/paths/"
run-pipeline:
	.venv/bin/python ./ml-pipeline/main.py \
		--input_datastore $(primary_datastore) \
		--output_datastore $(output_datastore)


# Commit local branch changes
branch=$(shell git symbolic-ref --short HEAD)
now=$(shell date '+%F_%H:%M:%S' )
git-push:
	git add . && git commit -m "Changes as of $(now)" && git push -u origin $(branch)

git-pull:
	git pull origin $(branch)
