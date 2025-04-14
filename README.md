# resume-parser
This project focuses on designing, deploying, and evaluating a serverless pipeline that:
1.	Automatically Triggers whenever a new resume is uploaded to cloud storage.
2.	Extracts Key Fields such as candidate name, contact details, skills, and work experience using cloud-based AI services.
3.	Stores the parsed data in a scalable data warehouse for further filtering and analytics (e.g., BigQuery).

**Deployment**
gcloud functions deploy parse_resumes_all_files \
    --no-gen2 \
    --runtime python39 \
    --trigger-resource resume-parser-bucket-iitj \
    --trigger-event google.storage.object.finalize \
    --set-env-vars PROJECT_ID=resume-parser-453018,PROCESSOR_ID=d482e194d9468d6b,DATASET_ID=resume_data,TABLE_ID=resume_data_table \
    --region us-central1
