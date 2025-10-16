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
