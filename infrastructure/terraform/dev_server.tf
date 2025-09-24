# Development Server EC2 Instance
# Only created in development environment

variable "diagram_mode" {
  description = "Set to 1 for diagram generation, 0 for real deployment"
  type        = string
  default     = "0"
}

variable "static_ami_id" {
  description = "Static AMI ID for diagram generation"
  type        = string
  default     = "ami-12345678"
}

variable "dev_server_ami_id" {
  description = "AMI ID for dev server (real deployment)"
  type        = string
  default     = ""
}

locals {
  # Use static AMI for diagram mode, or env AMI, or data source AMI
  use_data_source = var.diagram_mode == "0" && length(var.dev_server_ami_id) == 0
  dev_server_ami = (
    var.diagram_mode == "1" ? var.static_ami_id : 
    length(var.dev_server_ami_id) > 0 ? var.dev_server_ami_id : 
    local.use_data_source ? data.aws_ami.ubuntu[0].id : var.static_ami_id
  )
}

## Data source for latest Ubuntu AMI (only used if diagram_mode==0 and no AMI ID set in .env)
data "aws_ami" "ubuntu" {
  count = local.use_data_source ? 1 : 0
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-lts-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# Security group for development server
resource "aws_security_group" "dev_server" {
  count = var.create_dev_server ? 1 : 0
  
  name_prefix = "${var.project_name}-${var.environment}-dev-server-"
  vpc_id      = aws_vpc.main.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # HTTP for development servers
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # HTTPS for development servers
  ingress {
    from_port   = 8443
    to_port     = 8443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # Node.js development server
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-dev-server-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

## For diagram generation, comment out AMI data source and use static AMI ID
# data "aws_ami" "ubuntu" {
#   most_recent = true
#   owners      = ["099720109477"]
#   filter {
#     name   = "name"
#     values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
#   }
#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }
# }

resource "aws_instance" "dev_server" {
  count = var.create_dev_server ? 1 : 0
  ami                     = local.dev_server_ami
  instance_type           = local.dev_server_instance_type
  key_name                = var.dev_server_key_name
  subnet_id               = aws_subnet.management[0].id
  vpc_security_group_ids  = [aws_security_group.dev_server[0].id]
  monitoring              = local.enable_detailed_monitoring
  root_block_device {
    volume_type           = "gp3"
    volume_size           = local.dev_server_volume_size
    delete_on_termination = true
    encrypted             = true
  }

  # User data script for initial setup
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    environment = var.environment
  }))

  tags = {
    Name        = "${var.project_name}-${var.environment}-dev-server"
    Environment = var.environment
    Type        = "development"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Elastic IP for dev server (optional, for consistent SSH access)
resource "aws_eip" "dev_server" {
  count = var.create_dev_server ? 1 : 0
  
  instance = aws_instance.dev_server[0].id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-dev-server-eip"
  }

  depends_on = [aws_internet_gateway.main]
}

# Output values for dev server
output "dev_server_public_ip" {
  description = "Public IP address of the development server"
  value       = var.create_dev_server ? aws_eip.dev_server[0].public_ip : null
}

output "dev_server_private_ip" {
  description = "Private IP address of the development server"
  value       = var.create_dev_server ? aws_instance.dev_server[0].private_ip : null
}

output "dev_server_ssh_command" {
  description = "SSH command to connect to development server"
  value       = var.create_dev_server ? "ssh -i ~/.ssh/${var.dev_server_key_name}.pem ubuntu@${aws_eip.dev_server[0].public_ip}" : null
}
