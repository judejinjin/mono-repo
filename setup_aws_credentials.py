#!/usr/bin/env python3
"""
AWS Credentials Setup Helper
This script helps you configure AWS credentials in the .env file for testing.
"""

import os
import getpass
from pathlib import Path

def setup_aws_credentials():
    """Interactive setup for AWS credentials in .env file."""
    print("🔧 AWS Credentials Setup for Personal Account Testing")
    print("=" * 55)
    
    # Get project root and .env path
    project_root = Path(__file__).parent
    env_file = project_root / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found! Please make sure the .env file exists.")
        return False
    
    print(f"📁 Found .env file at: {env_file}")
    print()
    
    # Get AWS credentials from user
    print("Please enter your AWS credentials for personal account testing:")
    print("(These will be stored in the .env file)")
    print()
    
    aws_access_key = input("AWS Access Key ID: ").strip()
    if not aws_access_key:
        print("❌ AWS Access Key ID is required!")
        return False
    
    aws_secret_key = getpass.getpass("AWS Secret Access Key: ").strip()
    if not aws_secret_key:
        print("❌ AWS Secret Access Key is required!")
        return False
    
    aws_region = input("AWS Region (default: us-east-1): ").strip() or "us-east-1"
    
    aws_session_token = input("AWS Session Token (optional, press Enter to skip): ").strip()
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update AWS credentials in .env file
    updated_lines = []
    credentials_updated = {
        'AWS_ACCESS_KEY_ID': False,
        'AWS_SECRET_ACCESS_KEY': False,
        'AWS_REGION': False,
        'AWS_DEFAULT_REGION': False,
        'AWS_SESSION_TOKEN': False
    }
    
    for line in lines:
        if line.startswith('AWS_ACCESS_KEY_ID='):
            updated_lines.append(f'AWS_ACCESS_KEY_ID={aws_access_key}\n')
            credentials_updated['AWS_ACCESS_KEY_ID'] = True
        elif line.startswith('AWS_SECRET_ACCESS_KEY='):
            updated_lines.append(f'AWS_SECRET_ACCESS_KEY={aws_secret_key}\n')
            credentials_updated['AWS_SECRET_ACCESS_KEY'] = True
        elif line.startswith('AWS_REGION='):
            updated_lines.append(f'AWS_REGION={aws_region}\n')
            credentials_updated['AWS_REGION'] = True
        elif line.startswith('AWS_DEFAULT_REGION='):
            updated_lines.append(f'AWS_DEFAULT_REGION={aws_region}\n')
            credentials_updated['AWS_DEFAULT_REGION'] = True
        elif line.startswith('AWS_SESSION_TOKEN='):
            if aws_session_token:
                updated_lines.append(f'AWS_SESSION_TOKEN={aws_session_token}\n')
            else:
                updated_lines.append('#AWS_SESSION_TOKEN=your_session_token_here\n')
            credentials_updated['AWS_SESSION_TOKEN'] = True
        else:
            updated_lines.append(line)
    
    # Add any missing credentials
    if not credentials_updated['AWS_ACCESS_KEY_ID']:
        updated_lines.append(f'AWS_ACCESS_KEY_ID={aws_access_key}\n')
    if not credentials_updated['AWS_SECRET_ACCESS_KEY']:
        updated_lines.append(f'AWS_SECRET_ACCESS_KEY={aws_secret_key}\n')
    if not credentials_updated['AWS_REGION']:
        updated_lines.append(f'AWS_REGION={aws_region}\n')
    if not credentials_updated['AWS_DEFAULT_REGION']:
        updated_lines.append(f'AWS_DEFAULT_REGION={aws_region}\n')
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print()
    print("✅ AWS credentials successfully configured in .env file!")
    print()
    
    # Test the configuration
    print("🧪 Testing AWS credential configuration...")
    try:
        # Import our config module to test loading
        import sys
        sys.path.insert(0, str(project_root))
        from config import get_aws_credentials, setup_aws_environment
        
        # Test credential loading
        creds = get_aws_credentials()
        if creds.get('aws_access_key_id') and creds.get('aws_secret_access_key'):
            print(f"✅ Credentials loaded successfully!")
            print(f"   Region: {creds.get('region_name')}")
            print(f"   Access Key: {creds.get('aws_access_key_id')[:8]}...")
            return True
        else:
            print("❌ Failed to load credentials from .env file")
            return False
    
    except Exception as e:
        print(f"⚠️  Warning: Could not test configuration: {e}")
        print("   Your credentials are saved, but please verify manually.")
        return True


def verify_aws_access():
    """Verify AWS access with the configured credentials."""
    print("\n🔍 Verifying AWS Access...")
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from config import get_boto3_session
        
        session = get_boto3_session()
        if not session:
            print("❌ Could not create AWS session")
            return False
        
        # Try to list S3 buckets as a simple test
        s3 = session.client('s3')
        response = s3.list_buckets()
        
        print(f"✅ AWS access verified! Found {len(response['Buckets'])} S3 buckets.")
        return True
    
    except ImportError as e:
        print(f"⚠️  boto3 not available: {e}")
        print("   Run: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ AWS access verification failed: {e}")
        print("   Please check your credentials and permissions.")
        return False


if __name__ == "__main__":
    print("AWS Credentials Setup for VPC Infrastructure Testing")
    print("=" * 55)
    print()
    
    if setup_aws_credentials():
        print("\n" + "=" * 55)
        verify_choice = input("\nWould you like to verify AWS access? (y/N): ").strip().lower()
        if verify_choice in ['y', 'yes']:
            verify_aws_access()
        
        print("\n🎉 Setup complete! You can now run:")
        print("   python build/build.py")
        print("   python deploy/deploy.py")
        print("\nYour AWS credentials will be automatically loaded from the .env file.")
    else:
        print("\n❌ Setup failed. Please try again.")
