# Outputs for Financial Reports Analysis System

# ===== Cloud Run Service URLs =====

output "frontend_url" {
  description = "Frontend Service URL"
  value       = module.cloud_run.frontend_url
}

output "orchestrator_url" {
  description = "Orchestrator Agent URL"
  value       = module.cloud_run.orchestrator_url
}

output "report_reader_url" {
  description = "Report Reader Agent URL"
  value       = module.cloud_run.report_reader_url
}

output "logic_understanding_url" {
  description = "Logic Understanding Agent URL"
  value       = module.cloud_run.logic_understanding_url
}

output "visualization_url" {
  description = "Visualization Agent URL"
  value       = module.cloud_run.visualization_url
}

# ===== Storage Resources =====

output "reports_bucket_name" {
  description = "Cloud Storage bucket for reports"
  value       = module.storage.reports_bucket_name
}

output "charts_bucket_name" {
  description = "Cloud Storage bucket for charts"
  value       = module.storage.charts_bucket_name
}

# ===== Pub/Sub Resources =====

output "tasks_topic_name" {
  description = "Pub/Sub topic for tasks"
  value       = module.pubsub.tasks_topic_name
}

output "results_topic_name" {
  description = "Pub/Sub topic for results"
  value       = module.pubsub.results_topic_name
}

# ===== IAM Resources =====

output "service_account_email" {
  description = "Service account email for microservices"
  value       = module.iam.service_account_email
}

# ===== Artifact Registry =====

output "artifact_registry_repository" {
  description = "Artifact Registry repository for Docker images"
  value       = google_artifact_registry_repository.docker_repo.name
}

output "artifact_registry_location" {
  description = "Artifact Registry location"
  value       = google_artifact_registry_repository.docker_repo.location
}

# ===== Cloud Build Triggers =====

output "cloud_build_trigger_ids" {
  description = "Cloud Build trigger IDs for each service"
  value       = module.cloud_build.trigger_ids
}

# ===== Quick Start Commands =====

output "quick_start_commands" {
  description = "Quick start commands for testing the system"
  value = <<-EOT
  
  🎉 Deployment Complete! 🎉
  
  === Service URLs ===
  Frontend:            ${module.cloud_run.frontend_url}
  Orchestrator:        ${module.cloud_run.orchestrator_url}
  Report Reader:       ${module.cloud_run.report_reader_url}
  Logic Understanding: ${module.cloud_run.logic_understanding_url}
  Visualization:       ${module.cloud_run.visualization_url}
  
  === Quick Test ===
  Run the interactive demo:
    cd /Users/sergejbykov/financial-reports-system
    ./scripts/interactive_demo.sh
  
  Or test manually:
    TOKEN=$(gcloud auth print-identity-token)
    curl -H "Authorization: Bearer $TOKEN" ${module.cloud_run.frontend_url}/health
  
  === Storage Resources ===
  Reports Bucket:  ${module.storage.reports_bucket_name}
  Charts Bucket:   ${module.storage.charts_bucket_name}
  
  === Pub/Sub Topics ===
  Tasks Topic:     ${module.pubsub.tasks_topic_name}
  Results Topic:   ${module.pubsub.results_topic_name}
  
  === Service Account ===
  Email: ${module.iam.service_account_email}
  
  === Next Steps ===
  1. Push code to GitHub main branch
  2. Cloud Build will automatically build and deploy
  3. Run ./scripts/interactive_demo.sh to test
  4. Check logs: gcloud logging read --limit 50 --format json
  
  === Documentation ===
  User Guide:        docs/USER_GUIDE.md
  OAuth Setup:       docs/GITHUB_OAUTH_SETUP.md
  Quick Start:       docs/QUICKSTART_USAGE.md
  
  Happy analyzing! 🚀📊
  EOT
}

# ===== Configuration Summary =====

output "configuration_summary" {
  description = "Summary of the deployed configuration"
  value = {
    project_id                = var.project_id
    region                    = var.region
    environment               = var.environment
    github_repo              = "${var.github_owner}/${var.github_repo}"
    artifact_registry        = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.name}"
    enable_reasoning_engine  = var.enable_reasoning_engine
    enable_authentication    = var.enable_authentication
  }
}
