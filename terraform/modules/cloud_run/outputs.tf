# Outputs for Cloud Run module

output "frontend_url" {
  description = "Frontend Service URL"
  value       = google_cloud_run_v2_service.services["frontend"].uri
}

output "orchestrator_url" {
  description = "Orchestrator Agent URL"
  value       = google_cloud_run_v2_service.services["orchestrator"].uri
}

output "report_reader_url" {
  description = "Report Reader Agent URL"
  value       = google_cloud_run_v2_service.services["report_reader"].uri
}

output "logic_understanding_url" {
  description = "Logic Understanding Agent URL"
  value       = google_cloud_run_v2_service.services["logic_understanding"].uri
}

output "visualization_url" {
  description = "Visualization Agent URL"
  value       = google_cloud_run_v2_service.services["visualization"].uri
}

output "service_names" {
  description = "Map of all service names"
  value = {
    for k, v in google_cloud_run_v2_service.services : k => v.name
  }
}
