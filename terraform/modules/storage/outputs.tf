# Outputs for Storage module

output "reports_bucket_name" {
  description = "Name of the reports bucket"
  value       = google_storage_bucket.reports_bucket.name
}

output "reports_bucket_url" {
  description = "URL of the reports bucket"
  value       = google_storage_bucket.reports_bucket.url
}

output "charts_bucket_name" {
  description = "Name of the charts bucket"
  value       = google_storage_bucket.charts_bucket.name
}

output "charts_bucket_url" {
  description = "URL of the charts bucket"
  value       = google_storage_bucket.charts_bucket.url
}
