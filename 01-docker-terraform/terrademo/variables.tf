variable "credentials" {
  description = "Path to the GCP credentials JSON file"
  default     = "./keys/terraform-demo-putopavel-1c49266c2d77.json"
}

variable "project_id" {
  description = "GCP Project ID"
  default     = "terraform-demo-putopavel"

}

variable "region" {
  description = "GCP Region"
  default     = "europe-southwest1" # Madrid, Spain 
}

variable "location" {
  description = "Project Location"
  default     = "EU"

}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "terraform_demo_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "terraform-demo-putopavel-terra-bucket"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}