# Outputs for IAM module

output "service_account_email" {
  description = "Email of the microservices service account"
  value       = google_service_account.microservices_sa.email
}

output "service_account_id" {
  description = "ID of the microservices service account"
  value       = google_service_account.microservices_sa.id
}

output "service_account_name" {
  description = "Name of the microservices service account"
  value       = google_service_account.microservices_sa.name
}
