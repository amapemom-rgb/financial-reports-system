# Cloud Run Services Module
# Deploys all microservices to Cloud Run

locals {
  services = {
    frontend = {
      name        = "frontend-service"
      cpu         = "1"
      memory      = "512Mi"
      concurrency = 80
    }
    orchestrator = {
      name        = "orchestrator-agent"
      cpu         = "1"
      memory      = "512Mi"
      concurrency = 80
    }
    report_reader = {
      name        = "report-reader-agent"
      cpu         = "2"
      memory      = "1Gi"
      concurrency = 40
    }
    logic_understanding = {
      name        = "logic-understanding-agent"
      cpu         = "2"
      memory      = "2Gi"
      concurrency = 20
    }
    visualization = {
      name        = "visualization-agent"
      cpu         = "1"
      memory      = "1Gi"
      concurrency = 40
    }
  }
}

# Cloud Run services
resource "google_cloud_run_v2_service" "services" {
  for_each = local.services

  name     = each.value.name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = var.service_account_email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo_name}/${each.value.name}:latest"

      resources {
        limits = {
          cpu    = each.value.cpu
          memory = each.value.memory
        }
      }

      # Environment variables
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      env {
        name  = "SERVICE_NAME"
        value = each.value.name
      }

      ports {
        container_port = 8080
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    max_instance_request_concurrency = each.value.concurrency
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# IAM policy to allow unauthenticated access (change if needed)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  for_each = local.services

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.services[each.key].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
