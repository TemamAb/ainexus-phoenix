terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "arbitrage-prod-vpc"
  }
}

# Kubernetes EKS Cluster
resource "aws_eks_cluster" "arbitrage_cluster" {
  name     = "arbitrage-production"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.27"

  vpc_config {
    subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

# Database Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "arbitrage-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "Arbitrage DB Subnet Group"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "arbitrage_db" {
  identifier             = "arbitrage-production"
  engine                 = "postgres"
  engine_version         = "14.0"
  instance_class         = "db.t3.large"
  allocated_storage      = 100
  storage_type           = "gp2"
  db_name                = "arbitrage_prod"
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  multi_az               = true
  backup_retention_period = 7
  skip_final_snapshot    = true

  tags = {
    Environment = "production"
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "arbitrage_workers" {
  name                 = "arbitrage-workers"
  min_size             = 2
  max_size             = 10
  desired_capacity     = 4
  vpc_zone_identifier  = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  health_check_type    = "EC2"

  launch_template {
    id      = aws_launch_template.arbitrage_worker.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "arbitrage-worker"
    propagate_at_launch = true
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "arbitrage-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Scale up when CPU exceeds 80%"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
}

resource "aws_autoscaling_policy" "scale_up" {
  name                   = "arbitrage-scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.arbitrage_workers.name
}
