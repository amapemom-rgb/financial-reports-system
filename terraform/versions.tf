# Terraform and Provider Version Constraints

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
