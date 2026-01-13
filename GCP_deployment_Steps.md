# How to setup a GCP Cloud Run for your FastAPI app, using Docker containerization. 

# Phase 1: The Safety Net (Billing & Project)
Before we touch any code, we must ensure you never get an unexpected bill.

**Create a GCP Project**: Go into your Google Cloud Console and create a project named solar-forecasting-monitor.

**Set a Budget Alert**:

Search for "**Billing**" in the top search bar.

Go to **Budgets & Alerts > Create Budget**.

Set the amount to **$1.00**.

Set the threshold to **50%**. You will now get an email the moment your project costs even **$0.50**.

# Phase 2: Prepare Your Local Environment 
You need the Google Cloud CLI (command line interface) on your Mac to "talk" to GCP.

**1. Install the CLI**:

**Bash**:

brew install --cask google-cloud-sdk

**2. Initialize & Login**:

**Bash**:

gcloud init

- Follow the prompts to log into your Google account and select your solar-forecasting-monitor project.

**3. Enable the Necessary APIs**: Run this command to turn on the "Cloud Run" and "Artifact Registry" features for your project:

**Bash**:

gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Phase 3: Push to Artifact Registry
GCP cannot see the images on your laptop. You must "upload" your Docker image to a private library called Artifact Registry.

**1. Create the Repository**:

**Bash**:

gcloud artifacts repositories create solar-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Solar model and monitoring images"

**2. Configure Docker to talk to GCP**:

**Bash**:

gcloud auth configure-docker us-central1-docker.pkg.dev

**3. Tag and Push your Image**: Replace PROJECT_ID with your actual GCP Project ID (found on your GCP dashboard).

**Bash**:

_Build specifically for the cloud_
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/solar-repo/solar-app:v1 .

_Push it to the cloud_
docker push us-central1-docker.pkg.dev/PROJECT_ID/solar-repo/solar-app:v1

# Phase 4: Deploy to Cloud Run
Now we tell GCP to turn that image into a live website.

Run this final command:

**Bash**:

gcloud run deploy solar-service \
    --image us-central1-docker.pkg.dev/PROJECT_ID/solar-repo/solar-app:v1 \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

# Phase 5: Test Your Live URL
Once the command finishes, it will give you a Service URL (e.g., https://solar-service-xyz.a.run.app).

- **To Predict**: Send a POST request to https://your-url.com/predict.

- **To Monitor**: Simply visit https://your-url.com/monitor in your browser.

### One small fix for the Cloud: GCP uses a random port (usually 8080), not always 8000. To make your code robust, update the last line of your Dockerfile to use the ${PORT} variable provided by GCP:

**Dockerfile**:

CMD exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

### A good fix for keeping a local project is creating a different branch for the github repository so that you can have two different dockerfiles for each branch, one with port 8000 (local) and one with port 8080 (cloud).

# Phase 6: Setting up Cloud Storage (The Data Hub)
Right now, the reference data is "hardcoded" inside the Docker image. To make it a real MLOps pipeline, we want the monitoring script to read from a **Bucket**.

**1. Create a Storage Bucket**: Bucket names must be globally unique.

**Bash**

gcloud storage buckets create gs://solar-data-[YOUR-NAME] --location=us-central1

**2. Upload your reference data**:

**Bash**

gcloud storage cp data/reference_data.csv gs://solar-data-[YOUR-NAME]/

# Phase 7: Update Python code to read from the bucket
To transition from local files to a professional cloud-based data pipeline, we need to update the Python code to speak "Google Cloud." We will replace local file reading with the google-cloud-storage library.

**1. Update requirements.txt**
First, add the library that allows Python to interact with your GCP Bucket:

**Plaintext**

_... existing requirements ..._
google-cloud-storage
gcsfs

**2. Update src/monitoring.py**
We need to modify how the report is saved. Instead of just saving it to a local folder, we will also upload a copy to the bucket so it’s permanently archived.

**Python**

import pandas as pd
from google.cloud import storage #
from evidently import Report, Dataset, DataDefinition, Regression
from evidently.presets import DataDriftPreset, RegressionPreset
from pathlib import Path
import os

def generate_drift_report(reference_df, current_df, bucket_name=None):
    # ... (Keep your existing report.run logic) ...
    
    # 5. Save the output locally first
    report_path = Path("reports/drift_report.html")
    report_path.parent.mkdir(exist_ok=True)
    evaluation.save_html(str(report_path))
    
    # 6. OPTIONAL: Upload to GCP Bucket for permanent storage
    if bucket_name:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob("reports/latest_drift_report.html")
        blob.upload_from_filename(str(report_path))
        print(f"☁️ Report archived in GCP bucket: gs://{bucket_name}/reports/latest_drift_report.html")

**3. Update simulate_drift.py**
This is where the biggest change happens. Instead of pd.read_csv("data/reference_data.csv"), the script will now pull from the live bucket.

**Python**

import pandas as pd
import numpy as np
import os
from src.monitoring import generate_drift_report

def run_simulation():
    # Define your bucket name (Use the one you created in Phase 6)
    BUCKET_NAME = os.getenv("DATA_BUCKET", "solar-data-davide") 
    
    # 1. Load data FROM GCP BUCKET using gcsfs
    # This works because gcsfs allows pandas to read 'gs://' paths directly
    print(f"📂 Fetching reference data from gs://{BUCKET_NAME}...")
    ref_df = pd.read_csv(f"gs://{BUCKET_NAME}/reference_data.csv")
    
    ref_df['DATE_TIME'] = pd.to_datetime(ref_df['DATE_TIME'])

    # ... (Keep your simulation/drift logic here) ...

    # 3. Generate the Report and upload a copy back to the bucket
    generate_drift_report(ref_df, prod_df, bucket_name=BUCKET_NAME)

**Why these changes are important:**

- **Environment Variables (os.getenv):** This is a professional practice. It means you can change your bucket name without editing your code, simply by changing a setting in the GCP console.

- **gcsfs:** This library is a "secret weapon" for data scientists. It makes a Google Cloud Bucket look just like a normal folder to Pandas, which simplifies your code significantly.

- **Archiving:** By uploading the HTML report back to the bucket, you create a historical record of every drift check, which is essential for auditing model performance over time.

# Phase 8: Setting permissions for Cloud Run
To give the Cloud Run service permission to read and write to your bucket, you need to run one command for each role.

**First**, we need to find the Cloud Run project's Project Number (not ID). You can find it on your GCP Dashboard or run _gcloud projects describe PROJECT_ID --format="value(projectNumber)"_.

The default service account for Cloud Run follows this format: _PROJECT_NUMBER-compute@developer.gserviceaccount.com_

**The One-Line Commands**
Run these in your terminal (replacing the bracketed values with your actual info):

**1. To Read Data (Reference CSV):**

**Bash**

gcloud storage buckets add-iam-policy-binding gs://BUCKET_NAME \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

**2. To Write Reports (HTML Output):**

**Bash**

gcloud storage buckets add-iam-policy-binding gs://BUCKET_NAME \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectUser"

**Why two roles?**

**- storage.objectViewer:** Allows your code to "see" and download the reference data.

**- storage.objectUser:** Allows your code to create and overwrite the HTML reports in the bucket.

**Pro-Tip: The "Shortcut"**
If you want to do it in exactly one command for both, you can use the Project-Level binding (this gives the service access to all buckets in your project, which is common for smaller projects):

**Bash**

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Phase 9: Automation the trigger 

Currently, you have to manually visit your-api.com/monitor to see if your model is drifting. We can use Cloud Scheduler to "ping" that URL automatically every day at 9:00 AM.

**1. Create the "Trigger" Service Account**
This is a dedicated digital identity for your Scheduler.

**Bash**

gcloud iam service-accounts create scheduler-trigger-sa \
    --display-name="Service Account to trigger Monitoring"

**2. Give it Permission to "Invoke" your API**
Tell GCP that this specific account is allowed to call your private Cloud Run service.

**Bash**

gcloud run services add-iam-policy-binding solar-service \
    --member="serviceAccount:scheduler-trigger-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker" \
    --region=us-central1

**3. Create the Secure Scheduler Job**
Now, run the command you had, but with the --oidc-service-account-email flag added. This tells the scheduler to "sign in" as the account we just created before hitting your URL.

**Bash**

gcloud scheduler jobs create http solar-daily-monitor \
    --schedule="0 9 * * *" \
    --uri="https://YOUR-CLOUDRUN-URL/monitor" \
    --http-method=GET \
    --location=us-central1 \
    --oidc-service-account-email="scheduler-trigger-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --oidc-token-audience="https://YOUR-CLOUDRUN-URL"

**Final Verification Diagram**

**Summary Checklist for Automation**

- Code Update: Pulling data from the GS Bucket instead of local folders.

- Permissions: Giving Cloud Run access to the Bucket (Viewer/User).

- Authentication: Creating a Service Account for the Scheduler.

- Scheduler: Creating the job with the OIDC token attached.

# Phase 10 & 11: CI/CD & Automated Retraining (Out of the scope of this project)

**CI/CD: The "Hands-Off" Update**

Right now, if you change your code, you have to manually rebuild and push the Docker image. The professional way: Connect your GitHub repository to Cloud Run.

- When you _git push_, GCP will automatically detect the change, rebuild your container, and redeploy it. This ensures your production model is always in sync with your latest code.

**Closing the Loop: Automated Retraining (Optional/Advanced)**
In a full-scale project, if the Evidently report detects "High Drift," it shouldn't just send an email— it should trigger a Retraining Job.

- Flow: Drift Detected → Trigger Cloud Function → Run training script on new data → Update model in the Bucket.
