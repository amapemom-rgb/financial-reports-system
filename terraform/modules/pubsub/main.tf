# Pub/Sub Module
# Creates topics and subscriptions for async messaging

# Topic for task distribution
resource "google_pubsub_topic" "tasks_topic" {
  name = "financial-reports-tasks"

  message_retention_duration = "604800s" # 7 days

  labels = {
    purpose    = "task-distribution"
    managed_by = "terraform"
  }
}

# Topic for results
resource "google_pubsub_topic" "results_topic" {
  name = "financial-reports-results"

  message_retention_duration = "604800s" # 7 days

  labels = {
    purpose    = "results-collection"
    managed_by = "terraform"
  }
}

# Subscription for orchestrator to receive task updates (PUSH to Cloud Run)
resource "google_pubsub_subscription" "orchestrator_tasks_sub" {
  name  = "orchestrator-tasks-sub"
  topic = google_pubsub_topic.tasks_topic.name

  ack_deadline_seconds = 60

  message_retention_duration = "604800s"
  retain_acked_messages      = false

  # Push configuration to Cloud Run orchestrator
  push_config {
    push_endpoint = "${var.orchestrator_url}/pubsub/push"
    
    oidc_token {
      service_account_email = var.service_account_email
    }
  }

  expiration_policy {
    ttl = "" # Never expire
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Subscription for results aggregation
resource "google_pubsub_subscription" "results_sub" {
  name  = "results-aggregation-sub"
  topic = google_pubsub_topic.results_topic.name

  ack_deadline_seconds = 60

  message_retention_duration = "604800s"
  retain_acked_messages      = false

  expiration_policy {
    ttl = "" # Never expire
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Dead letter topic for failed messages
resource "google_pubsub_topic" "dead_letter_topic" {
  name = "financial-reports-dead-letter"

  message_retention_duration = "2678400s" # 31 days

  labels = {
    purpose    = "dead-letter-queue"
    managed_by = "terraform"
  }
}

# Dead letter subscription
resource "google_pubsub_subscription" "dead_letter_sub" {
  name  = "dead-letter-sub"
  topic = google_pubsub_topic.dead_letter_topic.name

  ack_deadline_seconds       = 600
  message_retention_duration = "2678400s"
  retain_acked_messages      = true

  expiration_policy {
    ttl = "" # Never expire
  }
}
