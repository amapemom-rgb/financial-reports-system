resource "google_pubsub_topic" "topic" {
  name    = var.topic_name
  project = var.project_id

  message_retention_duration = "86400s" # 24 hours
}

resource "google_pubsub_subscription" "subscriptions" {
  for_each = toset(var.subscription_names)

  name    = each.value
  topic   = google_pubsub_topic.topic.name
  project = var.project_id

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "2678400s" # 31 days
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}
