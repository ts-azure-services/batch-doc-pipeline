# batch-doc-pipeline
The purpose of this repo is to setup a batch pipeline to process PDFs into text files leveraging Azure ML's native pipeline
capabilities and Azure Form Recognizer (soon to be Azure AI Document Intelligence). This is a custom version of this [repo](https://github.com/ts-azure-services/document-extraction-pipeline).

### Other considerations
- With PDF file names, ensure special characters like `+` don't cause issues while processing. This is not specifically handled in
  the above operations.
- Given the size of the PDF files being processed, this can sometimes lead to out of memory issues. Either change the compute
  configuration or have a way of filtering out larger items to process independently.
- As of the current update (May 2024), [azure-ai-form-recognizer](https://pypi.org/project/azure-ai-formrecognizer/) was version 3.1 and GA. Over time, however this will give way to
  [azure-ai-documentintelligence](https://pypi.org/project/azure-ai-documentintelligence/) which is currently version 4.0 and in preview. This repo uses the former.
- In terms of RBAC, both the Azure ML workspace and the service principal have `Contributor` access to the storage account.
  Additionally, the workspace has `Storage Blob Data Contributor` access to the storage account.
- Note about for Form Recognizer, you can [auto-scale](https://learn.microsoft.com/en-us/azure/ai-services/autoscale?tabs=portal) to avoid throttling issues.
