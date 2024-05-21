# ifndef VERBOSE
# .SILENT:
# endif

venv-setup:
	rm -rf .venv
	python3.11 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r ./requirements.txt

sub-init:
	echo "SUB_ID=<enter subscription name>" > sub.env


# Infrastructure setup
infra:
	./setup/create-resources.sh

create-cluster:
	.venv/bin/python ./setup/cluster.py

create-env:
	.venv/bin/python ./setup/env.py --name "form-rec-env" \
		--conda_file "./setup/form-rec-env.yml"


pdf_blob=$(shell cat variables.env | grep "BLOB_CONTAINER_PDF" | cut -d "=" -f 2 | xargs)
text_blob=$(shell cat variables.env | grep "BLOB_CONTAINER_TXT" | cut -d "=" -f 2 | xargs)
create-datastores:
	.venv/bin/python ./common/datastore.py --container_name $(pdf_blob) \
		--datastore_name "pdfinputfiles" \
		--datastore_desc "PDF input files"
	.venv/bin/python ./common/datastore.py --container_name $(text_blob) \
		--datastore_name "textfiles" \
		--datastore_desc "Final text files"

## If running in the cloud shell, upload the azure-ai-studio pdf
# Then, use the script below to generate several files and upload to blob
input_file="./azure-ai-studio.pdf"
number_of_pdfs=5
create-pdfs:
	rm -rf ./pdf-files
	mkdir -p ./pdf-files
	.venv/bin/python ./setup/create_pdfs.py --input_file=$(input_file) --number_of_pdfs=$(number_of_pdfs)

upload-files:
	.venv/bin/python ./setup/upload_data.py


# Run ML pipeline
run-pipeline:
	.venv/bin/python ./ml-pipeline/main.py


# Commit local branch changes
branch=$(shell git symbolic-ref --short HEAD)
now=$(shell date '+%F_%H:%M:%S' )
git-push:
	git add . && git commit -m "Changes as of $(now)" && git push -u origin $(branch)

git-pull:
	git pull origin $(branch)python ./pipeline-parallel/main.py
