# Terraform Infrastructure Setup Guide

Complete guide for deploying Financial Reports Analysis System using Terraform.

---

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Google Cloud SDK installed:**
   ```bash
   # Check if gcloud is installed
   gcloud --version
   
   # If not, install from: https://cloud.google.com/sdk/docs/install
   ```

2. **Terraform installed (>= 1.5.0):**
   ```bash
   # Check Terraform version
   terraform --version
   
   # If not, install from: https://www.terraform.io/downloads
   ```

3. **GCP Project created:**
   - Project ID: `financial-reports-ai-2024`
   - Billing enabled
   - You have Owner or Editor role

4. **Authentication configured:**
   ```bash
   # Login to GCP
   gcloud auth login
   
   # Set default project
   gcloud config set project financial-reports-ai-2024
   
   # Enable Application Default Credentials for Terraform
   gcloud auth application-default login
   ```

---

## 🚀 Quick Start (One-Time Setup)

### Step 1: GitHub OAuth Setup (5 minutes)

**This step must be done ONCE before running Terraform.**

Follow the detailed guide: [docs/GITHUB_OAUTH_SETUP.md](../docs/GITHUB_OAUTH_SETUP.md)

**Summary:**
1. Go to: https://console.cloud.google.com/cloud-build/triggers
2. Click "CREATE TRIGGER" → "CONNECT NEW REPOSITORY"
3. Select "GitHub (Cloud Build GitHub App)"
4. Authorize and install Google Cloud Build in GitHub
5. Select repository: `amapemom-rgb/financial-reports-system`
6. Get the connection ID:
   ```bash
   gcloud builds connections list --region=us-central1
   ```
7. Copy the full connection path (e.g., `projects/123.../connections/github-xxx`)

---

### Step 2: Create Terraform State Bucket

```bash
# Create bucket for Terraform state
gsutil mb -p financial-reports-ai-2024 -l us-central1 gs://financial-reports-terraform-state

# Enable versioning
gsutil versioning set on gs://financial-reports-terraform-state
```

---

### Step 3: Configure Terraform Variables

```bash
# Navigate to terraform directory
cd terraform

# Copy example tfvars file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

**Required changes in `terraform.tfvars`:**

```hcl
# Update this with your GitHub connection ID from Step 1
github_connection = "projects/YOUR_PROJECT_NUMBER/locations/global/connections/github-YOUR_CONNECTION_ID"

# Verify project ID (should be correct already)
project_id = "financial-reports-ai-2024"
```

---

### Step 4: Deploy Everything!

```bash
# Initialize Terraform (downloads providers and modules)
terraform init

# Preview what will be created
terraform plan

# Deploy! (this takes 5-10 minutes)
terraform apply
```

**Type `yes` when prompted.**

---

## ✅ What Gets Created

When you run `terraform apply`, it creates:

### Cloud Build (CI/CD)
- ✅ 5 Cloud Build triggers (one per microservice)
- ✅ Automatic deployment on push to `main` branch
- ✅ Service account for Cloud Build with necessary permissions

### Cloud Run (Compute)
- ✅ 5 Cloud Run services (all microservices)
- ✅ Auto-scaling configuration (0-10 instances)
- ✅ CPU and memory limits per service

### Storage
- ✅ Artifact Registry for Docker images
- ✅ Cloud Storage bucket for reports
- ✅ Cloud Storage bucket for visualization charts

### Messaging
- ✅ Pub/Sub topics for tasks and results
- ✅ Subscriptions with retry policies
- ✅ Dead letter queue for failed messages

### IAM & Security
- ✅ Service account for microservices
- ✅ IAM roles and permissions
- ✅ Secure service-to-service communication

### APIs
- ✅ All required GCP APIs enabled automatically

---

## 🔄 Continuous Deployment

After initial setup, deployment is **completely automatic**:

```bash
# Make changes to any service
cd services/frontend-service
nano main.py  # make your changes

# Commit and push
git add .
git commit -m "Update frontend service"
git push origin main

# Cloud Build automatically:
# 1. Detects changes in services/frontend-service/**
# 2. Triggers frontend-service build
# 3. Builds Docker image
# 4. Pushes to Artifact Registry
# 5. Deploys to Cloud Run
# 6. Zero downtime deployment!
```

**Check build status:**
```bash
gcloud builds list --limit=5
```

---

## 📊 Verify Deployment

After `terraform apply` completes:

### 1. Check Terraform Outputs

```bash
terraform output
```

You'll see all service URLs, bucket names, and helpful commands.

### 2. Test Services

```bash
# Use the interactive demo script
cd /Users/sergejbykov/financial-reports-system
./scripts/interactive_demo.sh

# Or test manually
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" \
  https://frontend-service-<PROJECT_NUMBER>.us-central1.run.app/health
```

### 3. Check Cloud Build Triggers

```bash
gcloud builds triggers list --region=us-central1
```

You should see 5 triggers:
- `frontend-service-deploy`
- `orchestrator-agent-deploy`
- `report-reader-agent-deploy`
- `logic-understanding-agent-deploy`
- `visualization-agent-deploy`

---

## 🛠️ Common Commands

### View Current State
```bash
terraform show
```

### Update Infrastructure
```bash
# After changing .tf files
terraform plan
terraform apply
```

### Destroy Everything
```bash
# ⚠️ WARNING: This deletes ALL resources
terraform destroy
```

### View Specific Output
```bash
terraform output frontend_url
terraform output -json | jq
```

### Refresh State
```bash
terraform refresh
```

---

## 🔧 Troubleshooting

### Problem: "Error creating Trigger: Connection not found"

**Solution:** You didn't complete GitHub OAuth setup. Follow [docs/GITHUB_OAUTH_SETUP.md](../docs/GITHUB_OAUTH_SETUP.md)

### Problem: "Backend initialization required"

**Solution:**
```bash
terraform init -reconfigure
```

### Problem: "API not enabled"

**Solution:** Terraform should enable APIs automatically, but if it fails:
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Problem: "Permission denied"

**Solution:** Ensure you have the required roles:
```bash
gcloud projects add-iam-policy-binding financial-reports-ai-2024 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/owner"
```

### Problem: Terraform hangs during apply

**Solution:** Check Cloud Build logs:
```bash
gcloud builds list --ongoing
```

---

## 📁 Terraform Structure

```
terraform/
├── main.tf                  # Main configuration
├── variables.tf             # Variable definitions
├── outputs.tf              # Output definitions
├── versions.tf             # Provider versions
├── terraform.tfvars        # Your values (gitignored)
├── terraform.tfvars.example # Example values
│
└── modules/
    ├── cloud_build/        # Build triggers
    ├── cloud_run/          # Microservices
    ├── storage/            # Buckets
    ├── pubsub/             # Messaging
    └── iam/                # Permissions
```

---

## 🔐 Security Best Practices

1. **Never commit `terraform.tfvars`** (contains sensitive data)
2. **Use service accounts** for automation
3. **Enable audit logging:**
   ```bash
   gcloud logging read "protoPayload.serviceName=\"cloudbuild.googleapis.com\""
   ```
4. **Restrict IAM permissions** after initial setup
5. **Enable VPC Service Controls** for production

---

## 📚 Additional Resources

- **Terraform Google Provider:** https://registry.terraform.io/providers/hashicorp/google/latest/docs
- **Cloud Run Documentation:** https://cloud.google.com/run/docs
- **Cloud Build Documentation:** https://cloud.google.com/build/docs
- **Project Documentation:** [../USER_GUIDE.md](../USER_GUIDE.md)

---

## 🎉 Next Steps

After successful deployment:

1. **Test the system:** Run `./scripts/interactive_demo.sh`
2. **Upload a report:** Use option 3 in the menu
3. **Check logs:** `gcloud logging read --limit 50`
4. **Monitor costs:** https://console.cloud.google.com/billing
5. **Set up monitoring:** Configure Cloud Monitoring alerts

---

**🚀 You're ready to go! One `terraform apply` and everything is automated!**
