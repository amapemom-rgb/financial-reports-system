output "topic_id" {
  description = "Pub/Sub topic ID"
  value       = google_pubsub_topic.topic.id
}

output "topic_name" {
  description = "Pub/Sub topic name"
  value       = google_pubsub_topic.topic.name
}

output "subscription_ids" {
  description = "Subscription IDs"
  value       = { for k, v in google_pubsub_subscription.subscriptions : k => v.id }
}
