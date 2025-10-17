# Cloud Storage Module
# Creates buckets for reports and charts

# Bucket for financial reports
resource "google_storage_bucket" "reports_bucket" {
  name          = "${var.project_id}-reports"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  labels = {
    purpose     = "financial-reports"
    managed_by  = "terraform"
  }
}

# Bucket for visualization charts
resource "google_storage_bucket" "charts_bucket" {
  name          = "${var.project_id}-charts"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  labels = {
    purpose     = "visualization-charts"
    managed_by  = "terraform"
  }
}
