# 🚀 Financial Reports Analysis System

**Version:** 1.0.0-rc1 | **Status:** 99% Ready for Production 🎉

AI-powered multi-agent system for analyzing financial reports using Google Cloud Platform and Vertex AI (Gemini 2.0).

## ✨ Latest Updates (2025-10-17)

🎊 **Interactive Demo Fixed!** Health checks now work perfectly.

**What's New:**
- ✅ Fixed `interactive_demo.sh` - all health checks working
- ✅ New `test_health.sh` script for quick service checks
- ✅ Improved error handling and HTTP status code reporting
- ✅ Verbose mode for debugging
- ✅ Token refresh for each request
- 📚 Complete documentation in `docs/BUGFIX_INTERACTIVE_SCRIPT.md`

## 🎯 Features

- 📊 **Multi-format support**: Excel, CSV, Google Sheets
- 🤖 **Vertex AI Reasoning Engine v2**: Advanced multi-step reasoning
- 📈 **Interactive visualizations**: Automatic chart generation
- 🎤 **Voice interface**: Speech-to-Text/Text-to-Speech
- ☁️ **Cloud-native**: Serverless architecture on GCP
- 📡 **Async processing**: Pub/Sub messaging
- 🔒 **Secure**: IAM-based authentication

## 🚀 Quick Start

### Test the Live System (2 minutes)

```bash
# Clone and test
git clone https://github.com/amapemom-rgb/financial-reports-system.git
cd financial-reports-system

# Quick health check
chmod +x scripts/test_health.sh
./scripts/test_health.sh

# Interactive demo
chmod +x scripts/interactive_demo.sh
./scripts/interactive_demo.sh
```

### Local Development (15 minutes)

```bash
# Setup environment
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh

# Run all services
docker-compose up
```

### GCP Deployment (30 minutes)

```bash
# Set your variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Deploy everything
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 📚 Documentation

### Getting Started
- 📖 [Testing Guide](TESTING_GUIDE.md) - Test the system in 5 minutes
- 📖 [User Guide](USER_GUIDE.md) - Complete usage guide
- 📖 [Quick Start](QUICKSTART_USAGE.md) - Get started fast

### Technical Documentation
- 🔧 [Bug Fix Details](docs/BUGFIX_INTERACTIVE_SCRIPT.md) - Latest fixes
- 🏗️ [Architecture](docs/AGENT_V1_VS_V2.md) - System design
- 🚀 [Deployment Guide](DEPLOYMENT_GUIDE.md) - Deploy to GCP
- 📊 [Status](STATUS.md) - Project status (99% ready!)

### Reference
- 📋 [Action Plan](ACTION_PLAN.md) - Development roadmap
- 📝 [Cheatsheet](CHEATSHEET.md) - Quick commands

## 🏗️ Architecture

**5 Microservices (Cloud Run):**

| Service | Purpose | Tech Stack |
|---------|---------|------------|
| **Frontend** | API & Voice interface | FastAPI, Google Speech API |
| **Orchestrator** | Workflow coordination | Python, Pub/Sub |
| **Report Reader** | File parsing | Pandas, OpenPyXL |
| **Logic Agent** | AI analysis | Vertex AI Reasoning Engine v2 |
| **Visualization** | Chart generation | Matplotlib, Plotly |

**Key Technologies:**
- ☁️ Google Cloud Run (serverless)
- 🤖 Vertex AI Gemini 2.0 Flash
- 📡 Cloud Pub/Sub (async messaging)
- 🗄️ Cloud Storage (file storage)
- 🔐 Cloud IAM (authentication)

## 🎬 Demo

### Health Check
```bash
$ ./scripts/test_health.sh

🏥 Checking health of all services...

Frontend:            ✅ healthy
Orchestrator:        ✅ healthy
Report Reader:       ✅ healthy
Logic Agent:         ✅ healthy
Visualization:       ✅ healthy

✅ All services are healthy!
```

### Interactive Demo
```bash
$ ./scripts/interactive_demo.sh

🚀 Financial Reports System - Quick Start
==========================================

Выберите действие:
  1. 🏥 Проверить здоровье всех сервисов
  2. 📊 Создать тестовый CSV файл
  3. 📤 Загрузить файл и запустить анализ
  4. 📈 Создать визуализацию
  ...
```

## 📦 What's Deployed

**Live Services (GCP Cloud Run):**
- ✅ Frontend: `frontend-service-38390150695.us-central1.run.app`
- ✅ Orchestrator: `orchestrator-agent-38390150695.us-central1.run.app`
- ✅ Reader: `report-reader-agent-38390150695.us-central1.run.app`
- ✅ Logic: `logic-understanding-agent-38390150695.us-central1.run.app`
- ✅ Visualization: `visualization-agent-38390150695.us-central1.run.app`

**Status:** All services running and healthy! 🎉

## 🧪 Testing

```bash
# Quick health check (30 seconds)
./scripts/test_health.sh

# Full E2E test (5 minutes)
./scripts/test_e2e.sh

# Interactive testing (your pace)
./scripts/interactive_demo.sh
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed instructions.

## 💰 Cost Estimate

| Environment | Monthly Cost | Notes |
|-------------|--------------|-------|
| Development | $10-25 | Low traffic, test data |
| Production | $200-600 | Regular usage |

**Cost optimization tips:**
- Use Cloud Run's pay-per-use model
- Enable auto-scaling (0 to N instances)
- Set memory limits appropriately
- Use Cloud Storage lifecycle policies

## 🤝 Contributing

This is a production-ready system. For contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📋 Requirements

- **GCP Account** with billing enabled
- **gcloud CLI** configured
- **Docker** (for local development)
- **Python 3.11+**
- **Terraform** (optional, for IaC)

## 🔗 Links

- 📊 [Project Status](STATUS.md) - 99% ready!
- 🐛 [Latest Fixes](docs/BUGFIX_INTERACTIVE_SCRIPT.md)
- 📖 [Full Documentation](USER_GUIDE.md)
- 🎯 [Roadmap](ACTION_PLAN.md)

## 🆘 Support

**Having issues?**

1. Check [TESTING_GUIDE.md](TESTING_GUIDE.md) troubleshooting section
2. Review [docs/BUGFIX_INTERACTIVE_SCRIPT.md](docs/BUGFIX_INTERACTIVE_SCRIPT.md)
3. Open an issue on GitHub

**Common problems:**
- Token issues: `gcloud auth login`
- Permission errors: Check IAM roles
- Service errors: Check Cloud Run logs

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

**🎊 System is 99% ready for production! Start testing now!**

Made with ❤️ using Google Cloud Platform and Vertex AI
