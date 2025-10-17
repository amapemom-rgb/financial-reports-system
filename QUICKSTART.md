# 🚀 Quick Start - Financial Reports Analysis System

**Automated deployment with ONE command: `terraform apply`**

---

## ⚡ TL;DR

```bash
# 1. Complete GitHub OAuth (5 min, one-time)
#    See: docs/GITHUB_OAUTH_SETUP.md

# 2. Configure Terraform (2 min)
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Add your GitHub connection ID

# 3. Deploy everything (8 min)
terraform init
terraform apply  # Type 'yes'

# 4. Done! Test the system
cd ..
./scripts/interactive_demo.sh
```

---

## 📚 Complete Documentation

### 🎯 Start Here
- **[DEPLOYMENT_MASTER_PLAN.md](DEPLOYMENT_MASTER_PLAN.md)** - Complete deployment guide
- **[TERRAFORM_AUTOMATION_SUMMARY.md](TERRAFORM_AUTOMATION_SUMMARY.md)** - What was automated

### 📖 Detailed Guides
- **[docs/GITHUB_OAUTH_SETUP.md](docs/GITHUB_OAUTH_SETUP.md)** - GitHub OAuth setup (one-time)
- **[terraform/README.md](terraform/README.md)** - Terraform usage guide
- **[USER_GUIDE.md](USER_GUIDE.md)** - System usage guide
- **[QUICKSTART_USAGE.md](QUICKSTART_USAGE.md)** - Quick start examples

### 📊 Status & Info
- **[STATUS.md](STATUS.md)** - Current project status
- **[PRODUCTION_READY.md](PRODUCTION_READY.md)** - Production checklist

---

## 🏗️ What Gets Deployed

### ✅ Infrastructure (Terraform)
- 5 Cloud Run microservices
- 5 Cloud Build triggers (auto-deploy)
- Artifact Registry (Docker images)
- Cloud Storage (reports & charts)
- Pub/Sub (messaging)
- IAM (permissions)

### ✅ CI/CD Pipeline
- Push to `main` → automatic deployment
- Zero downtime deployments
- Per-service triggers

---

## 🔄 Workflow

### One-Time Setup (15 minutes)
1. GitHub OAuth setup (manual, 5 min)
2. Configure `terraform.tfvars` (2 min)
3. Run `terraform apply` (8 min)

### Every Future Deployment (Automatic)
```bash
git push origin main
# Done! Cloud Build handles the rest
```

---

## 📁 Project Structure

```
financial-reports-system/
├── DEPLOYMENT_MASTER_PLAN.md      # 👈 START HERE
├── terraform/                      # Infrastructure as Code
│   ├── main.tf
│   ├── modules/
│   │   ├── cloud_build/           # CI/CD triggers
│   │   ├── cloud_run/             # Microservices
│   │   ├── storage/               # Buckets
│   │   ├── pubsub/                # Messaging
│   │   └── iam/                   # Permissions
│   └── README.md
├── services/                       # Microservices code
│   ├── frontend-service/
│   │   ├── Dockerfile
│   │   ├── cloudbuild.yaml
│   │   └── main.py
│   ├── orchestrator-agent/
│   ├── report-reader-agent/
│   ├── logic-understanding-agent/
│   └── visualization-agent/
├── docs/
│   └── GITHUB_OAUTH_SETUP.md
└── scripts/
    └── interactive_demo.sh
```

---

## ✅ Prerequisites

- [ ] GCP Project: `financial-reports-ai-2024`
- [ ] Billing enabled
- [ ] gcloud CLI installed & authenticated
- [ ] Terraform >= 1.5.0 installed
- [ ] GitHub repo: `amapemom-rgb/financial-reports-system`

---

## 🎉 Features

- ✅ **One-command deployment** - `terraform apply`
- ✅ **Auto-scaling** - 0-10 instances per service
- ✅ **Cost-optimized** - Scale to zero when idle
- ✅ **Production-ready** - Health checks, logging, monitoring
- ✅ **Version controlled** - All infrastructure in Git
- ✅ **Zero downtime** - Rolling deployments

---

## 📞 Quick Links

- **Deploy:** [DEPLOYMENT_MASTER_PLAN.md](DEPLOYMENT_MASTER_PLAN.md)
- **OAuth Setup:** [docs/GITHUB_OAUTH_SETUP.md](docs/GITHUB_OAUTH_SETUP.md)
- **Terraform Guide:** [terraform/README.md](terraform/README.md)
- **Usage Guide:** [USER_GUIDE.md](USER_GUIDE.md)

---

**Ready to deploy? Read [DEPLOYMENT_MASTER_PLAN.md](DEPLOYMENT_MASTER_PLAN.md) for the complete guide!** 🚀
