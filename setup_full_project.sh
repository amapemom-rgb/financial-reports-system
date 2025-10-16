#!/bin/bash
echo "🚀 Создание файлов проекта"

# Terraform Pub/Sub
mkdir -p terraform/modules/pubsub
echo 'variable "project_id" { type = string }' > terraform/modules/pubsub/main.tf
echo "✓ Pub/Sub модуль"

# Terraform Storage  
mkdir -p terraform/modules/storage
echo 'variable "project_id" { type = string }' > terraform/modules/storage/main.tf
echo "✓ Storage модуль"

# Setup script
cat > scripts/setup_local.sh << 'EOF'
#!/bin/bash
echo "🚀 Setup local environment"
if ! command -v docker &> /dev/null; then
    echo "Docker not installed"
    exit 1
fi
echo "Starting Docker..."
docker-compose up -d
echo "Done!"
EOF
chmod +x scripts/setup_local.sh
echo "✓ setup_local.sh"

# Test script
cat > scripts/test_local.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing..."
docker-compose ps
EOF
chmod +x scripts/test_local.sh
echo "✓ test_local.sh"

# Docs
echo "# Quick Start" > QUICKSTART.md
echo "# Cheatsheet" > CHEATSHEET.md
echo "✓ Documentation"

echo ""
echo "✅ Готово!"
echo "Выполните: git add . && git commit -m 'Add files' && git push"
