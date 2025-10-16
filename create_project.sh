#!/bin/bash
set -e

echo "🚀 Создание структуры проекта Financial Reports System..."

# Создание директорий
echo "📁 Создание директорий..."
mkdir -p agents/{frontend-service,orchestrator-agent,report-reader-agent,logic-understanding-agent,visualization-agent}
mkdir -p terraform/{modules/{pubsub,storage,cloudsql,cloudrun,secrets,iam,load-balancer,monitoring},environments/dev}
mkdir -p scripts
mkdir -p tests/{integration,load}
mkdir -p docs
mkdir -p shared/{common,schemas,clients}
mkdir -p .github/workflows

echo "✅ Структура создана"

# Создание базовых файлов
echo "📝 Создание базовых файлов..."

# .gitignore уже создан GitHub'ом, дополним его
cat >> .gitignore << 'EOF'

# Project specific
deployment_info.json
deploy.log
.env
.env.local
terraform.tfstate*
.terraform/
postgres_data/
storage_data/
EOF

# docker-compose.yml
cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: financial-reports-db
    environment:
      POSTGRES_DB: financial_reports
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  pubsub-emulator:
    image: gcr.io/google.com/cloudsdktool/cloud-sdk:emulators
    container_name: financial-reports-pubsub
    command: gcloud beta emulators pubsub start --host-port=0.0.0.0:8085
    ports:
      - "8085:8085"
    environment:
      PUBSUB_PROJECT_ID: local-project

  storage-emulator:
    image: fsouza/fake-gcs-server
    container_name: financial-reports-storage
    ports:
      - "4443:4443"
    command: -scheme http -port 4443 -external-url http://localhost:4443
    volumes:
      - storage_data:/data

volumes:
  postgres_data:
  storage_data:

networks:
  default:
    name: financial-reports-network
DOCKEREOF

echo "✅ Docker Compose создан"

# Основной README
cat > README.md << 'READMEEOF'
# 🚀 Financial Reports Analysis System

AI-powered multi-agent system for analyzing financial reports using Google Cloud Platform and Vertex AI (Gemini).

## 🎯 Features

- 📊 Reads Excel and Google Sheets
- 🤖 AI-powered analysis with Gemini
- 📈 Interactive visualizations
- 🎤 Voice interface (Speech-to-Text/Text-to-Speech)
- ☁️ Cloud-native (serverless)
- 📡 Async processing with Pub/Sub

## 🚀 Quick Start

### Local Development (15 minutes)

\`\`\`bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/financial-reports-system.git
cd financial-reports-system

# Setup and run
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
\`\`\`

### GCP Deployment (30 minutes)

\`\`\`bash
# Set variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export ALERT_EMAIL="your@email.com"

# Deploy
chmod +x scripts/deploy_gcp_step_by_step.sh
./scripts/deploy_gcp_step_by_step.sh
\`\`\`

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Step-by-Step Guide](STEP_BY_STEP_GUIDE.md)
- [Cheatsheet](CHEATSHEET.md)
- [Action Plan](ACTION_PLAN.md)

## 🏗️ Architecture

5 microservices (agents):
1. **Frontend Service** - API & Voice interface
2. **Orchestrator Agent** - Task coordination
3. **Report Reader Agent** - File parsing
4. **Logic Understanding Agent** - AI analysis (Gemini)
5. **Visualization Agent** - Chart generation

## 💰 Cost

- **Development**: ~$10-25/month
- **Production**: ~$200-600/month

## 📄 License

MIT License - see LICENSE file
READMEEOF

echo "✅ README создан"
echo ""
echo "🎉 Базовая структура готова!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Добавьте Gemini API key в .env файл"
echo "2. Запустите: docker-compose up -d"
echo "3. Проверьте: curl http://localhost:5432 (PostgreSQL)"
echo ""
echo "📖 Для создания остальных файлов используйте артефакты из чата с Claude"
echo ""

