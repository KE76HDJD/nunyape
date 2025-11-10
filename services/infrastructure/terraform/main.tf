module "vpc" {
  source = "./modules/vpc"

  name               = "payment-app"
  cidr_block         = "10.0.0.0/16"
  public_subnets     = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets    = ["10.0.10.0/24", "10.0.20.0/24"]
  availability_zones = ["us-west-2a", "us-west-2b"]
}

module "eks" {
  source = "./modules/eks"

  cluster_name = "payment-cluster"
  subnet_ids   = module.vpc.private_subnet_ids
  desired_size = 2
  max_size     = 5
  min_size     = 1
}

module "rds" {
  source = "./modules/rds"

  identifier             = "payment-db"
  instance_class         = "db.t3.medium"
  allocated_storage      = 20
  db_name               = "paymentdb"
  username              = "paymentuser"
  password              = var.db_password
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  subnet_ids            = module.vpc.private_subnet_ids
}

module "s3" {
  source = "./modules/s3"

  bucket_name = "payment-app-backups-${random_id.bucket_suffix.hex}"
  versioning = true
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}