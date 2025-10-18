# 🚀 DEPLOYMENT MASTER PLAN

**One-Command Infrastructure Deployment for Financial Reports Analysis System**

---

## 🎯 Goal

Deploy the entire Financial Reports Analysis System with **ONE COMMAND**: `terraform apply`

After initial one-time manual GitHub OAuth setup, everything else is automated.

---

## 📊 What You Get

### ✅ Fully Automated CI/CD Pipeline
- Push to `main` → Automatic build → Automatic deploy
- Zero downtime deployments
- Rollback capabilities

### ✅ Complete Infrastructure
- 5 Cloud Run microservices
- Cloud Build triggers
- Artifact Registry
- Cloud Storage buckets
- Pub/Sub messaging
- IAM roles and permissions

### ✅ Production-Ready Setup
- Auto-scaling (0-10 instances)
- Health checks
- Logging and monitoring
- Secure service-to-service auth

---

## 📋 Prerequisites Checklist

- [ ] GCP Project created: `financial-reports-ai-2024`
- [ ] Billing enabled on the project
- [ ] gcloud CLI installed and authenticated
- [ ] Terraform >= 1.5.0 installed
- [ ] GitHub repository: `amapemom-rgb/financial-reports-system`
- [ ] You have Owner or Editor role in GCP project

---

## 🔐 ONE-TIME MANUAL STEP: GitHub OAuth

**Time required:** 5 minutes  
**Frequency:** Once (never again)

### Why Manual?

Terraform cannot automatically complete OAuth authorization (requires browser interaction).

### How to Do It

**Option A: Quick Instructions**

1. Open: https://console.cloud.google.com/cloud-build/triggers
2. Click "CREATE TRIGGER" → "CONNECT NEW REPOSITORY"
3. Select "GitHub (Cloud Build GitHub App)"
4. Authorize Google Cloud Build in GitHub
5. Select repository: `amapemom-rgb/financial-reports-system`
6. Cancel trigger creation (Terraform will create triggers)
7. Get connection ID:
   ```bash
   gcloud builds connections list --region=us-central1
   ```
8. Copy full path (e.g., `projects/123.../connections/github-abc123`)

**Option B: Detailed Guide**

See: [docs/GITHUB_OAUTH_SETUP.md](docs/GITHUB_OAUTH_SETUP.md)

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Authenticate with GCP

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project financial-reports-ai-2024

# Setup application default credentials for Terraform
gcloud auth application-default login
```

---

### Step 2: Create Terraform State Bucket

```bash
# Create bucket for storing Terraform state
gsutil mb -p financial-reports-ai-2024 -l us-central1 \
  gs://financial-reports-terraform-state

# Enable versioning (important for state history)
gsutil versioning set on gs://financial-reports-terraform-state
```

---

### Step 3: Complete GitHub OAuth (One-Time)

Follow the instructions in: [docs/GITHUB_OAUTH_SETUP.md](docs/GITHUB_OAUTH_SETUP.md)

**Result:** You get a connection ID like:
```
projects/123456789/locations/global/connections/github-abc123def456
```

---

### Step 4: Configure Terraform

```bash
# Clone repository (if not already)
git clone https://github.com/amapemom-rgb/financial-reports-system.git
cd financial-reports-system/terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Update these values in `terraform.tfvars`:**

```hcl
# REQUIRED: Your GitHub connection from Step 3
github_connection = "projects/YOUR_PROJECT_NUMBER/locations/global/connections/github-YOUR_ID"

# VERIFY: Project ID (should already be correct)
project_id = "financial-reports-ai-2024"

# OPTIONAL: Customize if needed
region = "us-central1"
environment = "prod"
```

---

### Step 5: Deploy Everything! 🎉

```bash
# Initialize Terraform (downloads providers)
terraform init

# Preview changes (optional but recommended)
terraform plan

# Deploy everything!
terraform apply
```

**When prompted, type:** `yes`

**Deployment time:** 5-10 minutes

---

## ✅ What Happens During `terraform apply`

### Phase 1: Enable APIs (1-2 min)
- Cloud Run API
- Cloud Build API
- Artifact Registry API
- Pub/Sub API
- Cloud Storage API
- Vertex AI API
- Secret Manager API

### Phase 2: Create Base Infrastructure (2-3 min)
- Artifact Registry repository
- Cloud Storage buckets (reports, charts)
- Pub/Sub topics and subscriptions
- Service accounts
- IAM role bindings

### Phase 3: Setup CI/CD (1-2 min)
- 5 Cloud Build triggers
- Cloud Build service account
- Build permissions

### Phase 4: Deploy Services (2-3 min)
- 5 Cloud Run services (placeholders initially)
- Service configurations
- Public access policies

### Phase 5: Outputs (< 1 min)
- Service URLs
- Bucket names
- Quick start commands

---

## 📊 Verify Deployment

### 1. Check Terraform Output

```bash
terraform output
```

You should see:
```
frontend_url = "https://frontend-service-xxxxx.us-central1.run.app"
orchestrator_url = "https://orchestrator-agent-xxxxx.us-central1.run.app"
...
quick_start_commands = "..."
```

### 2. Verify Cloud Build Triggers

```bash
gcloud builds triggers list --region=us-central1
```

Expected output:
```
NAME                           CREATE_TIME                STATUS
frontend-service-deploy        2025-10-17T15:00:00        ENABLED
orchestrator-agent-deploy      2025-10-17T15:00:00        ENABLED
report-reader-agent-deploy     2025-10-17T15:00:00        ENABLED
logic-understanding-agent-...  2025-10-17T15:00:00        ENABLED
visualization-agent-deploy     2025-10-17T15:00:00        ENABLED
```

### 3. Test Services

```bash
# Use the interactive demo
./scripts/interactive_demo.sh

# Or test manually
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" \
  $(terraform output -raw frontend_url)/health
```

Expected response:
```json
{"status":"healthy","service":"frontend-service"}
```

---

## 🔄 Continuous Deployment Workflow

After initial setup, **every push to main automatically deploys**:

```bash
# 1. Make changes to any service
cd services/frontend-service
nano main.py

# 2. Commit and push
git add .
git commit -m "feat: Add new endpoint"
git push origin main

# 3. Automatic magic happens:
#    ✅ Cloud Build detects changes
#    ✅ Builds Docker image
#    ✅ Pushes to Artifact Registry
#    ✅ Deploys to Cloud Run
#    ✅ Zero downtime!
```

**Monitor builds:**
```bash
# Watch builds in real-time
gcloud builds list --ongoing

# View specific build logs
gcloud builds log <BUILD_ID>
```

---

## 📁 Project Structure

```
financial-reports-system/
├── services/                          # Microservices code
│   ├── frontend-service/
│   │   ├── main.py
│   │   ├── Dockerfile                 # ✅ Created
│   │   ├── cloudbuild.yaml           # ✅ Created
│   │   └── requirements.txt
│   ├── orchestrator-agent/
│   │   ├── main.py
│   │   ├── Dockerfile                 # ✅ Created
│   │   ├── cloudbuild.yaml           # ✅ Created
│   │   └── requirements.txt
│   ├── report-reader-agent/          # Same structure
│   ├── logic-understanding-agent/    # Same structure
│   └── visualization-agent/          # Same structure
│
├── terraform/                         # Infrastructure as Code
│   ├── main.tf                       # ✅ Created
│   ├── variables.tf                  # ✅ Created
│   ├── outputs.tf                    # ✅ Created
│   ├── versions.tf                   # ✅ Created
│   ├── terraform.tfvars.example      # ✅ Created
│   ├── terraform.tfvars              # YOU create this
│   ├── README.md                     # ✅ Created
│   │
│   └── modules/
│       ├── cloud_build/              # ✅ Created
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── cloud_run/                # ✅ Created
│       ├── storage/                  # ✅ Created
│       ├── pubsub/                   # ✅ Created
│       └── iam/                      # ✅ Created
│
├── docs/
│   ├── GITHUB_OAUTH_SETUP.md        # ✅ Created
│   ├── USER_GUIDE.md
│   └── DEPLOYMENT_MASTER_PLAN.md    # ✅ This file
│
└── scripts/
    ├── interactive_demo.sh           # ✅ Fixed
    └── test_health.sh
```

---

## 🛠️ Common Operations

### Update Infrastructure

```bash
cd terraform

# After modifying .tf files
terraform plan
terraform apply
```

### View Logs

```bash
# Service logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Build logs
gcloud logging read "resource.type=build" --limit 50
```

### Rollback a Service

```bash
# List revisions
gcloud run revisions list --service=frontend-service --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic frontend-service \
  --to-revisions=frontend-service-00002-abc=100 \
  --region=us-central1
```

### Scale a Service

```bash
gcloud run services update frontend-service \
  --min-instances=1 \
  --max-instances=20 \
  --region=us-central1
```

### Destroy Everything

```bash
# ⚠️ WARNING: Deletes ALL resources
cd terraform
terraform destroy
```

---

## 🐛 Troubleshooting

### Issue: "Connection not found" during terraform apply

**Cause:** GitHub OAuth not completed  
**Fix:** Complete Step 3 (GitHub OAuth Setup)

### Issue: "Permission denied" errors

**Cause:** Insufficient GCP permissions  
**Fix:**
```bash
gcloud projects add-iam-policy-binding financial-reports-ai-2024 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/owner"
```

### Issue: Build fails with "image not found"

**Cause:** First deployment, images don't exist yet  
**Fix:** Push code to trigger initial builds:
```bash
git commit --allow-empty -m "Trigger initial build"
git push origin main
```

### Issue: Service returns 503

**Cause:** Service not fully deployed or crashed  
**Fix:**
```bash
# Check service status
gcloud run services describe frontend-service --region=us-central1

# View logs
gcloud logging read "resource.type=cloud_run_revision 
  resource.labels.service_name=frontend-service" --limit 50
```

---

## 📊 Cost Estimation

### Monthly costs (approximate):

- **Cloud Run:** $0-50 (depends on traffic, scale-to-zero saves costs)
- **Cloud Storage:** $1-5 (90-day lifecycle policy)
- **Cloud Build:** $0 (120 free builds/day)
- **Artifact Registry:** $0.10/GB stored
- **Pub/Sub:** $0-10 (first 10GB free)
- **Vertex AI:** Pay-per-use (Gemini API calls)

**Total estimated:** $10-100/month depending on usage

**Free tier benefits:**
- Cloud Build: 120 builds/day free
- Cloud Run: 2M requests/month free
- Cloud Storage: 5GB free
- Pub/Sub: 10GB/month free

---

## 🔐 Security Considerations

### ✅ Implemented
- Service accounts with least-privilege IAM roles
- Cloud Run with IAM authentication
- Secure service-to-service communication
- API keys in Secret Manager
- Audit logging enabled

### 🔄 Recommended for Production
- Enable VPC Service Controls
- Setup Cloud Armor for DDoS protection
- Configure Cloud KMS for encryption
- Enable Binary Authorization
- Setup Security Command Center

---

## 📚 Documentation Links

- **Terraform Setup:** [terraform/README.md](terraform/README.md)
- **GitHub OAuth:** [docs/GITHUB_OAUTH_SETUP.md](docs/GITHUB_OAUTH_SETUP.md)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Quick Start:** [QUICKSTART_USAGE.md](QUICKSTART_USAGE.md)

---

## 🎉 Summary

### Your deployment workflow:

```bash
# ONE-TIME SETUP (15 minutes)
1. GitHub OAuth → 5 min
2. Configure terraform.tfvars → 2 min
3. terraform init && terraform apply → 8 min

# DONE! ✅
```

### Every future deployment:

```bash
# ONGOING DEPLOYMENTS (automatic)
git push origin main
# That's it! Cloud Build handles the rest.
```

---

## ✅ Success Checklist

After completing all steps, you should have:

- [ ] All 5 Cloud Build triggers created and enabled
- [ ] All 5 Cloud Run services deployed and healthy
- [ ] Artifact Registry repository with Docker images
- [ ] Cloud Storage buckets for reports and charts
- [ ] Pub/Sub topics and subscriptions configured
- [ ] Service account with proper IAM roles
- [ ] Interactive demo script working (`./scripts/interactive_demo.sh`)
- [ ] Health checks returning 200 OK
- [ ] Automatic deployments working (test with a dummy commit)

---

## 🚀 You're Ready!

**Your entire infrastructure is now:**
- ✅ Version controlled (Terraform)
- ✅ Automatically deployed (Cloud Build)
- ✅ Production ready (auto-scaling, monitoring)
- ✅ Easy to maintain (one command updates)

**Happy deploying! 🎊**

Need help? Check:
- [terraform/README.md](terraform/README.md) - Detailed Terraform guide
- [docs/GITHUB_OAUTH_SETUP.md](docs/GITHUB_OAUTH_SETUP.md) - OAuth setup
- [USER_GUIDE.md](USER_GUIDE.md) - System usage guide
