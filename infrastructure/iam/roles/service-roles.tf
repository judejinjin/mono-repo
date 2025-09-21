# Service Roles for AWS Services
# EKS, Lambda, RDS, and other AWS service roles

# EKS Cluster Service Role
resource "aws_iam_role" "eks_cluster_role" {
  name = "${local.name_prefix}-eks-cluster-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-eks-cluster-role"
    Description = "Service role for EKS cluster operations"
    Service     = "EKS"
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster_role.name
}

# EKS Node Group Role
resource "aws_iam_role" "eks_node_group_role" {
  name = "${local.name_prefix}-eks-node-group-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-eks-node-group-role"
    Description = "Service role for EKS node group instances"
    Service     = "EKS"
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_readonly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group_role.name
}

# Instance Profile for EKS Node Group
resource "aws_iam_instance_profile" "eks_node_group" {
  name = "${local.name_prefix}-eks-node-group-profile"
  role = aws_iam_role.eks_node_group_role.name

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-eks-node-group-profile"
    Description = "Instance profile for EKS node group"
    Service     = "EKS"
  })
}

# Lambda Execution Roles (one per function)
resource "aws_iam_role" "lambda_execution_role" {
  for_each = toset(var.lambda_functions)
  
  name = "${local.name_prefix}-lambda-${each.key}-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-lambda-${each.key}-role"
    Description = "Execution role for ${each.key} Lambda function"
    Service     = "Lambda"
    Function    = each.key
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  for_each = toset(var.lambda_functions)
  
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role[each.key].name
}

# RDS Enhanced Monitoring Role
resource "aws_iam_role" "rds_monitoring_role" {
  name = "${local.name_prefix}-rds-monitoring-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-rds-monitoring-role"
    Description = "Enhanced monitoring role for RDS instances"
    Service     = "RDS"
  })
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
  role       = aws_iam_role.rds_monitoring_role.name
}

# EC2 Instance Role for Bastion Host
resource "aws_iam_role" "bastion_host_role" {
  name = "${local.name_prefix}-bastion-host-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-bastion-host-role"
    Description = "Role for bastion host EC2 instances"
    Service     = "EC2"
  })
}

resource "aws_iam_role_policy_attachment" "bastion_ssm_managed_instance" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.bastion_host_role.name
}

resource "aws_iam_role_policy_attachment" "bastion_cloudwatch_agent" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role       = aws_iam_role.bastion_host_role.name
}

# Instance Profile for Bastion Host
resource "aws_iam_instance_profile" "bastion_host" {
  name = "${local.name_prefix}-bastion-host-profile"
  role = aws_iam_role.bastion_host_role.name

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-bastion-host-profile"
    Description = "Instance profile for bastion host"
    Service     = "EC2"
  })
}

# CodeBuild Service Role
resource "aws_iam_role" "codebuild_role" {
  name = "${local.name_prefix}-codebuild-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-codebuild-role"
    Description = "Service role for CodeBuild projects"
    Service     = "CodeBuild"
  })
}

resource "aws_iam_role_policy_attachment" "codebuild_base_policy" {
  policy_arn = "arn:aws:iam::aws:policy/CodeBuildDeveloperAccess"
  role       = aws_iam_role.codebuild_role.name
}

# CodePipeline Service Role
resource "aws_iam_role" "codepipeline_role" {
  name = "${local.name_prefix}-codepipeline-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-codepipeline-role"
    Description = "Service role for CodePipeline"
    Service     = "CodePipeline"
  })
}

resource "aws_iam_role_policy_attachment" "codepipeline_service_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AWSCodePipelineServiceRole"
  role       = aws_iam_role.codepipeline_role.name
}

# Application Load Balancer Controller Role (for EKS)
resource "aws_iam_role" "alb_controller_role" {
  name = "${local.name_prefix}-alb-controller-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${local.account_id}:oidc-provider/${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}"
        }
        Condition = {
          StringEquals = {
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:kube-system:aws-load-balancer-controller"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-alb-controller-role"
    Description = "Service role for AWS Load Balancer Controller in EKS"
    Service     = "EKS"
    Component   = "ALB-Controller"
  })
}

# EBS CSI Driver Role (for EKS)
resource "aws_iam_role" "ebs_csi_driver_role" {
  name = "${local.name_prefix}-ebs-csi-driver-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${local.account_id}:oidc-provider/${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}"
        }
        Condition = {
          StringEquals = {
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:sub" = "system:serviceaccount:kube-system:ebs-csi-controller-sa"
            "${replace(var.eks_cluster_name, "${local.name_prefix}-", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-ebs-csi-driver-role"
    Description = "Service role for EBS CSI driver in EKS"
    Service     = "EKS"
    Component   = "EBS-CSI"
  })
}

resource "aws_iam_role_policy_attachment" "ebs_csi_driver_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
  role       = aws_iam_role.ebs_csi_driver_role.name
}
