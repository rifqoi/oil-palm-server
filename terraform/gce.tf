resource "google_compute_address" "gce_sa_ip_addr" {
  name = "backend-public-ip"
}

resource "google_compute_address" "gce_sa_ip_addr_frontend" {
  name = "frontend-public-ip"
}

/* resource "google_service_account" "gce_sa_backend" { */
/*   account_id   = "gce_sa_backend" */
/*   display_name = "GCE Service Account Backend" */
/* } */

# FIREWALL WEB SERVER PORTS
resource "google_compute_firewall" "web-server" {
  name      = "web-server"
  network   = "default"
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8000", "42000"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

resource "google_compute_instance" "gce_instance" {
  name         = "oil-palm-server"
  machine_type = "e2-standard-2"
  zone         = "asia-southeast1-b"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-pro-cloud/ubuntu-pro-2004-lts"
      size  = 20
      type  = "pd-ssd"
    }
  }

  tags = ["web-server"]

  network_interface {
    network = "default"

    access_config {
      nat_ip = google_compute_address.gce_sa_ip_addr.address
    }
  }

  metadata_startup_script = file("./install-docker.sh")
}

resource "google_compute_instance" "gce_frontend_server" {
  name         = "oil-palm-frontend"
  machine_type = "e2-medium"
  zone         = "asia-southeast1-b"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-pro-cloud/ubuntu-pro-2004-lts"
      size  = 20
      type  = "pd-ssd"
    }
  }

  tags = ["web-server"]

  network_interface {
    network = "default"

    access_config {
      nat_ip = google_compute_address.gce_sa_ip_addr_frontend.address
    }
  }

  metadata_startup_script = file("./install-docker.sh")
}
