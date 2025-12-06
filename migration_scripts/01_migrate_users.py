#!/usr/bin/env python3
"""
User Migration Script - Old Database to Supabase

This script migrates users from the HeyProData Excel file to Supabase.
It creates:
  - auth.users entries (with email authentication)
  - user_profiles (with name, bio, profile photo)
  - user_roles (from categories)
  - user_links (from URLs)

Usage:
  python 01_migrate_users.py

Requirements:
  - pip install supabase pandas openpyxl
  - HeyProData Member Info.xlsx in the same directory
  - Supabase credentials in environment or this file
"""

import os
import sys
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import re
import time

# Supabase Configuration
SUPABASE_URL = "https://kvidydsfnnrathhpuxye.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt2aWR5ZHNmbm5yYXRoaHB1eHllIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzYxMjc1OCwiZXhwIjoyMDc5MTg4NzU4fQ.oDbAaN2hrEQni0VW8wsKiRqZDbqlnS_Lj-fJ4OsIefo"

# Excel file path
EXCEL_FILE = "HeyProData_Member_Info.xlsx"


class UserMigration:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        self.migration_log = []
        self.success_count = 0
        self.error_count = 0
        
    def sanitize_name(self, name):
        """Split name into first_name and surname"""
        if pd.isna(name) or not name:
            return "Unknown", "User"
        
        name_parts = str(name).strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else "Unknown"
        surname = name_parts[1] if len(name_parts) > 1 else ""
        
        return first_name, surname
    
    def generate_email(self, name, index):
        """Generate email from name if not provided"""
        # Create email-friendly version of name
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', str(name).lower())
        email = f"{clean_name}_{index}@heypro.migration"
        return email
    
    def parse_categories(self, categories):
        """Parse categories string into list of roles"""
        if pd.isna(categories) or not categories:
            return []
        
        # Split by comma and clean
        roles = [role.strip() for role in str(categories).split(',')]
        return [role for role in roles if role]  # Remove empty strings
    
    def create_auth_user(self, email, name):
        """Create user in auth.users table"""
        try:
            # Use Supabase Admin API to create user
            # This creates a user without password (they'll use magic link)
            response = self.supabase.auth.admin.create_user({
                "email": email,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": {
                    "full_name": name,
                    "migrated_from": "HeyProData",
                    "migrated_at": datetime.now().isoformat()
                }
            })
            
            return response.user.id, None
        except Exception as e:
            return None, str(e)
    
    def create_user_profile(self, user_id, first_name, surname, bio, logo_url):
        """Create user profile"""
        try:
            profile_data = {
                "user_id": user_id,
                "first_name": first_name,
                "surname": surname,
                "bio": bio if not pd.isna(bio) else None,
                "profile_photo_url": logo_url if not pd.isna(logo_url) else None,
                "is_profile_complete": False,
                "profile_completion_percentage": 30,  # Base percentage for migrated users
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            response = self.supabase.table('user_profiles').insert(profile_data).execute()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def create_user_roles(self, user_id, roles):
        """Create user roles from categories"""
        if not roles:
            return True, None
        
        try:
            roles_data = [
                {
                    "user_id": user_id,
                    "role_name": role,
                    "sort_order": idx,
                    "created_at": datetime.now().isoformat()
                }
                for idx, role in enumerate(roles)
            ]
            
            response = self.supabase.table('user_roles').insert(roles_data).execute()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def create_user_link(self, user_id, url):
        """Create user link"""
        if pd.isna(url) or not url:
            return True, None
        
        try:
            link_data = {
                "user_id": user_id,
                "label": "Profile Link",
                "url": str(url),
                "sort_order": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            response = self.supabase.table('user_links').insert(link_data).execute()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def migrate_user(self, row, index):
        """Migrate a single user"""
        name = row.get('Name', '')
        url = row.get('URL', '')
        tagline = row.get('Tagline', '')
        categories = row.get('Categories', '')
        logo = row.get('Logo', '')
        
        # Generate email (we don't have emails in the CSV)
        email = self.generate_email(name, index)
        
        # Parse name
        first_name, surname = self.sanitize_name(name)
        
        # Parse roles
        roles = self.parse_categories(categories)
        
        log_entry = {
            "index": index,
            "name": name,
            "email": email,
            "status": "processing"
        }
        
        print(f"\n[{index}] Migrating: {name} ({email})")
        
        # Step 1: Create auth user
        print("  → Creating auth user...")
        user_id, error = self.create_auth_user(email, name)
        if error:
            log_entry["status"] = "failed"
            log_entry["error"] = f"Auth creation failed: {error}"
            print(f"  ✗ Failed: {error}")
            self.error_count += 1
            self.migration_log.append(log_entry)
            return False
        
        log_entry["user_id"] = user_id
        print(f"  ✓ Auth user created: {user_id}")
        
        # Step 2: Create user profile
        print("  → Creating user profile...")
        success, error = self.create_user_profile(user_id, first_name, surname, tagline, logo)
        if not success:
            log_entry["status"] = "partial"
            log_entry["error"] = f"Profile creation failed: {error}"
            print(f"  ✗ Failed: {error}")
            self.error_count += 1
            self.migration_log.append(log_entry)
            return False
        
        print("  ✓ User profile created")
        
        # Step 3: Create user roles
        if roles:
            print(f"  → Creating {len(roles)} roles...")
            success, error = self.create_user_roles(user_id, roles)
            if not success:
                print(f"  ⚠ Roles creation warning: {error}")
            else:
                print(f"  ✓ Roles created: {', '.join(roles)}")
        
        # Step 4: Create user link
        if url and not pd.isna(url):
            print("  → Creating user link...")
            success, error = self.create_user_link(user_id, url)
            if not success:
                print(f"  ⚠ Link creation warning: {error}")
            else:
                print("  ✓ User link created")
        
        log_entry["status"] = "success"
        print(f"  ✓ Migration complete")
        self.success_count += 1
        self.migration_log.append(log_entry)
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
        
        return True
    
    def run_migration(self):
        """Main migration process"""
        print("="*70)
        print("USER MIGRATION: HeyProData → Supabase")
        print("="*70)
        
        # Check if Excel file exists
        if not os.path.exists(EXCEL_FILE):
            print(f"\n✗ Error: Excel file not found: {EXCEL_FILE}")
            print(f"  Please place the file in: {os.path.abspath(EXCEL_FILE)}")
            return
        
        # Read Excel file
        print(f"\n→ Reading Excel file: {EXCEL_FILE}")
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name='Content')
            print(f"  ✓ Found {len(df)} users to migrate")
        except Exception as e:
            print(f"  ✗ Failed to read Excel file: {e}")
            return
        
        # Filter out empty rows
        df = df.dropna(subset=['Name'])
        print(f"  ✓ {len(df)} valid users after filtering")
        
        # Confirm migration
        print(f"\n⚠ WARNING: This will create {len(df)} new users in Supabase")
        confirm = input("  Continue? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("  Migration cancelled.")
            return
        
        # Migrate users
        print(f"\n→ Starting migration...\n")
        start_time = time.time()
        
        for index, row in df.iterrows():
            self.migrate_user(row, index + 1)
        
        # Summary
        duration = time.time() - start_time
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"Total users processed: {len(df)}")
        print(f"✓ Successful: {self.success_count}")
        print(f"✗ Failed: {self.error_count}")
        print(f"⏱ Duration: {duration:.2f} seconds")
        print("="*70)
        
        # Save log
        log_df = pd.DataFrame(self.migration_log)
        log_file = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        log_df.to_csv(log_file, index=False)
        print(f"\n→ Migration log saved: {log_file}")
        
        print("\n✓ Migration complete!")
        print("\nNext steps:")
        print("  1. Run script 02_generate_magic_links.py to generate magic links")
        print("  2. Send magic links to users via email\n")


if __name__ == "__main__":
    try:
        migration = UserMigration()
        migration.run_migration()
    except KeyboardInterrupt:
        print("\n\n⚠ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
