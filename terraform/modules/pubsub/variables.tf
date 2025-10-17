variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "topic_name" {
  description = "Pub/Sub topic name"
  type        = string
}

variable "subscription_names" {
  description = "List of subscription names"
  type        = list(string)
  default     = []
}
