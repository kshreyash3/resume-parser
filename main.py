from google.cloud import storage, documentai, bigquery
import json
import os

# Hardcoded variables (for testing only!)
PROCESSOR_ID = os.getenv("PROCESSOR_ID", "d482e194d9468d6b")
PROJECT_ID = os.getenv("PROJECT_ID", "resume-parser-453018")
DATASET_ID = os.getenv("DATASET_ID", "resume_data")
TABLE_ID = os.getenv("TABLE_ID", "resume_data_table")

def clean_field_name(field_name):
    """Standardize field names to match BigQuery schema."""
    return field_name.lower().strip().replace(" ", "_").replace(":", "")

def parse_resumes(bucket_name, file_name, processor_id, project_id, dataset_id, table_id):
    """Parses a resume using Document AI and stores the results in BigQuery."""

    # Initialize Google Cloud clients
    storage_client = storage.Client()
    documentai_client = documentai.DocumentProcessorServiceClient()
    bigquery_client = bigquery.Client()

    # Download file from GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    file_content = blob.download_as_bytes()

    # Process document using Document AI
    name = f"projects/{project_id}/locations/us/processors/{processor_id}"
    raw_document = documentai.RawDocument(content=file_content, mime_type="application/pdf")
    process_request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = documentai_client.process_document(request=process_request)
    document = result.document

    # Prepare data for BigQuery
    data_to_insert = {"filename": file_name}
    for page in document.pages:
        for form_field in page.form_fields:
            field_name = clean_field_name(form_field.field_name.text_anchor.content)
            field_value = form_field.field_value.text_anchor.content.strip()

            # Insert only if field matches the BigQuery schema
            if field_name in ["name", "email", "phone", "skills", "experience"]:
                data_to_insert[field_name] = field_value

    # Insert into BigQuery
    table_ref = bigquery_client.dataset(dataset_id).table(table_id)
    rows_to_insert = [data_to_insert]
    errors = bigquery_client.insert_rows_json(table_ref, rows_to_insert)

    if errors:
        print(f"BigQuery Insertion Errors for {file_name}: {errors}")
    else:
        print(f"Successfully inserted data for {file_name} into BigQuery.")

def parse_resumes_all_files(event, context):
    """Triggered when a file is uploaded to Cloud Storage."""
    
    bucket_name = event["bucket"]
    file_name = event["name"]

    # Process only relevant file types
    if file_name.endswith(('.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg')):
        parse_resumes(bucket_name, file_name, PROCESSOR_ID, PROJECT_ID, DATASET_ID, TABLE_ID)
