provider "google" {
  project = "norse-decoder-387302"
  region  = "asia-southeast1"
}

terraform {
  backend "gcs" {
    bucket = "rifqoi-tf-state"
    prefix = "terraform/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}


