# Administrative User Accounts
# High-privilege admin users with comprehensive access

# Administrative Users
resource "aws_iam_user" "admins" {
  for_each = {
    for user in var.admin_users : user.name => user
  }
  
  name          = "${local.name_prefix}-admin-${each.value.name}"
  path          = "/administrators/"
  force_destroy = false  # Protect admin accounts from accidental deletion

  tags = merge(local.common_tags, {
    Name       = "${local.name_prefix}-admin-${each.value.name}"
    Email      = each.value.email
    Role       = each.value.role
    UserType   = "administrator"
    Department = "it-security"
  })
}

# Admin User Login Profiles (Console Access Required)
resource "aws_iam_user_login_profile" "admins" {
  for_each = {
    for user in var.admin_users : user.name => user
  }
  
  user                    = aws_iam_user.admins[each.key].name
  password_reset_required = true
  password_length         = max(var.password_policy.minimum_password_length, 16)  # Higher security for admins

  lifecycle {
    ignore_changes = [password_reset_required]
  }
}

# Admin Access Keys (Limited and Monitored)
resource "aws_iam_access_key" "admins" {
  for_each = {
    for user in var.admin_users : user.name => user
    if user.role == "security-admin" || user.role == "platform-admin"
  }
  
  user = aws_iam_user.admins[each.key].name
  
  depends_on = [aws_iam_user.admins]
}

# Store Admin Access Keys in Secrets Manager with High Security
resource "aws_secretsmanager_secret" "admin_access_keys" {
  for_each = {
    for user in var.admin_users : user.name => user
    if user.role == "security-admin" || user.role == "platform-admin"
  }
  
  name        = "${local.name_prefix}-admin-${each.key}-access-key"
  description = "Access key for administrator ${each.key}"
  kms_key_id  = aws_kms_key.admin_secrets_key.id
  
  tags = merge(local.common_tags, {
    Name     = "${local.name_prefix}-admin-${each.key}-access-key"
    UserType = "administrator"
    Role     = each.value.role
    Security = "high"
  })
}

resource "aws_secretsmanager_secret_version" "admin_access_keys" {
  for_each = {
    for user in var.admin_users : user.name => user
    if user.role == "security-admin" || user.role == "platform-admin"
  }
  
  secret_id = aws_secretsmanager_secret.admin_access_keys[each.key].id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.admins[each.key].id
    secret_access_key = aws_iam_access_key.admins[each.key].secret
    user_name         = aws_iam_user.admins[each.key].name
    email             = each.value.email
    role              = each.value.role
  })
}

# KMS Key for Admin Secrets
resource "aws_kms_key" "admin_secrets_key" {
  description             = "KMS key for admin secrets encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnableRootAccess"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowAdminAccess"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.admin_users : aws_iam_user.admins[user.name].arn
          ]
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-admin-secrets-key"
    Description = "KMS key for admin secrets encryption"
    Purpose     = "admin-security"
  })
}

resource "aws_kms_alias" "admin_secrets_key_alias" {
  name          = "alias/${local.name_prefix}-admin-secrets"
  target_key_id = aws_kms_key.admin_secrets_key.key_id
}

# Admin MFA Devices (Mandatory for Admins)
resource "aws_iam_virtual_mfa_device" "admins" {
  for_each = {
    for user in var.admin_users : user.name => user
  }
  
  virtual_mfa_device_name = "${local.name_prefix}-admin-${each.key}-mfa"
  path                    = "/administrators/"

  tags = merge(local.common_tags, {
    Name     = "${local.name_prefix}-admin-${each.key}-mfa"
    UserType = "administrator"
    Role     = each.value.role
  })
}

# Super Admin Role (Full AWS Access)
resource "aws_iam_role" "super_admin_role" {
  name = "${local.name_prefix}-super-admin-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.admin_users : aws_iam_user.admins[user.name].arn
            if user.role == "super-admin"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
          IpAddress = {
            "aws:SourceIp" = var.office_ip_ranges
          }
          NumericLessThan = {
            "aws:TokenIssueTime" = "900"  # Token must be issued within last 15 minutes
          }
        }
      }
    ]
  })

  max_session_duration = 3600  # 1 hour maximum

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-super-admin-role"
    Description = "Full administrative access role"
    AccessLevel = "super-admin"
    Security    = "critical"
  })
}

resource "aws_iam_role_policy_attachment" "super_admin_access" {
  policy_arn = local.managed_policies.administrator_access
  role       = aws_iam_role.super_admin_role.name
}

# Security Admin Role (Security-Focused Access)
resource "aws_iam_role" "security_admin_role" {
  name = "${local.name_prefix}-security-admin-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.admin_users : aws_iam_user.admins[user.name].arn
            if user.role == "security-admin"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
          IpAddress = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  max_session_duration = var.session_duration

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-security-admin-role"
    Description = "Security administration role"
    AccessLevel = "security-admin"
    Focus       = "security"
  })
}

resource "aws_iam_role_policy_attachment" "security_admin_access" {
  policy_arn = local.managed_policies.security_audit
  role       = aws_iam_role.security_admin_role.name
}

# Platform Admin Role (Infrastructure Management)
resource "aws_iam_role" "platform_admin_role" {
  name = "${local.name_prefix}-platform-admin-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.admin_users : aws_iam_user.admins[user.name].arn
            if user.role == "platform-admin"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
          IpAddress = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  max_session_duration = var.session_duration

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-platform-admin-role"
    Description = "Platform and infrastructure administration role"
    AccessLevel = "platform-admin"
    Focus       = "infrastructure"
  })
}

resource "aws_iam_role_policy_attachment" "platform_admin_systems" {
  policy_arn = local.managed_policies.systems_administrator
  role       = aws_iam_role.platform_admin_role.name
}

resource "aws_iam_role_policy_attachment" "platform_admin_network" {
  policy_arn = local.managed_policies.network_administrator
  role       = aws_iam_role.platform_admin_role.name
}

# Database Admin Role (Database Management)
resource "aws_iam_role" "database_admin_role" {
  name = "${local.name_prefix}-database-admin-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.admin_users : aws_iam_user.admins[user.name].arn
            if user.role == "database-admin"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
          IpAddress = {
            "aws:SourceIp" = var.office_ip_ranges
          }
        }
      }
    ]
  })

  max_session_duration = var.session_duration

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-database-admin-role"
    Description = "Database administration role"
    AccessLevel = "database-admin"
    Focus       = "database"
  })
}

resource "aws_iam_role_policy_attachment" "database_admin_access" {
  policy_arn = local.managed_policies.database_administrator
  role       = aws_iam_role.database_admin_role.name
}

# Emergency Break-Glass Role (Emergency Access)
resource "aws_iam_role" "emergency_access_role" {
  name = "${local.name_prefix}-emergency-access-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = [
            for user in var.admin_users : aws_iam_user.admins[user.name].arn
            if user.role == "super-admin" || user.role == "security-admin"
          ]
        }
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
          # No IP restriction for emergency access
          NumericLessThan = {
            "aws:TokenIssueTime" = "300"  # Token must be very recent (5 minutes)
          }
        }
      }
    ]
  })

  max_session_duration = 1800  # 30 minutes maximum for emergency

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-emergency-access-role"
    Description = "Emergency break-glass access role"
    AccessLevel = "emergency"
    Purpose     = "disaster-recovery"
  })
}

resource "aws_iam_role_policy_attachment" "emergency_admin_access" {
  policy_arn = local.managed_policies.administrator_access
  role       = aws_iam_role.emergency_access_role.name
}

# CloudTrail for Admin Activity Monitoring
resource "aws_cloudtrail" "admin_activities" {
  name           = "${local.name_prefix}-admin-activities-trail"
  s3_bucket_name = aws_s3_bucket.admin_audit_logs.bucket

  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    exclude_management_event_sources = []

    data_resource {
      type = "AWS::IAM::Role"
      values = [
        aws_iam_role.super_admin_role.arn,
        aws_iam_role.security_admin_role.arn,
        aws_iam_role.platform_admin_role.arn,
        aws_iam_role.database_admin_role.arn,
        aws_iam_role.emergency_access_role.arn
      ]
    }
  }

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-admin-activities-trail"
    Description = "CloudTrail for admin activity monitoring"
    Purpose     = "security-audit"
  })
}

# S3 Bucket for Admin Audit Logs
resource "aws_s3_bucket" "admin_audit_logs" {
  bucket = "${local.name_prefix}-admin-audit-logs"

  tags = merge(local.common_tags, {
    Name        = "${local.name_prefix}-admin-audit-logs"
    Description = "Admin activity audit logs"
    Purpose     = "security-audit"
  })
}

resource "aws_s3_bucket_versioning" "admin_audit_versioning" {
  bucket = aws_s3_bucket.admin_audit_logs.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "admin_audit_encryption" {
  bucket = aws_s3_bucket.admin_audit_logs.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.admin_secrets_key.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "admin_audit_pab" {
  bucket = aws_s3_bucket.admin_audit_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
