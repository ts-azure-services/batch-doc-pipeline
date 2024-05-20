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
	.venv/bin/python ./setup/env.py --name "read-docs" \
		--conda_file "./config/form-rec-env.yml"

# Change default blob store to an ADLS by changing 'Hierarchial namespace'. Ensure above operation completes.
# Upload sample pdf files from /data/ to folder `pdf-inputs`, under the default blob store

## Local file testing
input_file="./azure-ai-studio.pdf"
number_of_pdfs=5
create-pdfs:
	rm -rf ./pdf-files
	mkdir -p ./pdf-files
	.venv/bin/python ./local-file-creation/create_pdfs.py --input_file=$(input_file) --number_of_pdfs=$(number_of_pdfs)

upload-files:
	.venv/bin/python ./local-file-creation/upload_data.py

data_input_file="./pdf-files/15035e58-dca0-49fa-928c-0f9dae008d92.pdf"
output_path="./pdf-files/sample.txt"
test-pdf:
	.venv/bin/python ./local-file-creation/pdf_model.py --data_input_file=$(data_input_file) \
		--output_path=$(output_path)


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
