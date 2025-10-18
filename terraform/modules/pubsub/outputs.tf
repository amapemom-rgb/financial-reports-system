# Outputs for Pub/Sub module

output "tasks_topic_name" {
  description = "Name of the tasks topic"
  value       = google_pubsub_topic.tasks_topic.name
}

output "tasks_topic_id" {
  description = "ID of the tasks topic"
  value       = google_pubsub_topic.tasks_topic.id
}

output "results_topic_name" {
  description = "Name of the results topic"
  value       = google_pubsub_topic.results_topic.name
}

output "results_topic_id" {
  description = "ID of the results topic"
  value       = google_pubsub_topic.results_topic.id
}

output "dead_letter_topic_name" {
  description = "Name of the dead letter topic"
  value       = google_pubsub_topic.dead_letter_topic.name
}

output "orchestrator_tasks_subscription" {
  description = "Name of the orchestrator tasks subscription"
  value       = google_pubsub_subscription.orchestrator_tasks_sub.name
}

output "results_subscription" {
  description = "Name of the results subscription"
  value       = google_pubsub_subscription.results_sub.name
}
