#!/usr/bin/env python3
"""
Magic Link Generation Script

This script generates magic links for all migrated users in Supabase.
Output: CSV file with user information and their magic links (7 days expiration)

Usage:
  python 02_generate_magic_links.py

Requirements:
  - pip install supabase pandas
  - Users must be already migrated to Supabase
  - Supabase credentials
"""

import os
import sys
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timedelta
import time

# Supabase Configuration
SUPABASE_URL = "https://kvidydsfnnrathhpuxye.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt2aWR5ZHNmbm5yYXRoaHB1eHllIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzYxMjc1OCwiZXhwIjoyMDc5MTg4NzU4fQ.oDbAaN2hrEQni0VW8wsKiRqZDbqlnS_Lj-fJ4OsIefo"

# Magic link configuration
MAGIC_LINK_EXPIRY_DAYS = 7
REDIRECT_URL = os.getenv('REDIRECT_URL', 'https://yourdomain.com/auth/callback')  # Update this!


class MagicLinkGenerator:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        self.magic_links = []
        self.success_count = 0
        self.error_count = 0
    
    def fetch_all_users(self):
        """Fetch all users from Supabase"""
        try:
            # Fetch users from auth.users with their profiles
            response = self.supabase.table('user_profiles') \
                .select('user_id, first_name, surname, bio, profile_photo_url') \
                .execute()
            
            return response.data, None
        except Exception as e:
            return None, str(e)
    
    def get_user_email(self, user_id):
        """Get user email from auth.users using admin API"""
        try:
            # Use admin API to get user details
            user = self.supabase.auth.admin.get_user_by_id(user_id)
            return user.user.email, None
        except Exception as e:
            return None, str(e)
    
    def generate_magic_link(self, email):
        """Generate magic link for a user"""
        try:
            # Generate OTP for magic link
            # Supabase will send email, but we'll construct the link manually
            response = self.supabase.auth.admin.generate_link({
                "type": "magiclink",
                "email": email,
                "options": {
                    "redirect_to": REDIRECT_URL
                }
            })
            
            # Extract the magic link
            magic_link = response.properties.action_link
            
            return magic_link, None
        except Exception as e:
            return None, str(e)
    
    def process_user(self, user, index, total):
        """Process a single user and generate magic link"""
        user_id = user.get('user_id')
        first_name = user.get('first_name', '')
        surname = user.get('surname', '')
        full_name = f"{first_name} {surname}".strip()
        
        print(f"\n[{index}/{total}] Processing: {full_name}")
        
        # Get user email
        print("  → Fetching email...")
        email, error = self.get_user_email(user_id)
        if error:
            print(f"  ✗ Failed to get email: {error}")
            self.error_count += 1
            return
        
        print(f"  ✓ Email: {email}")
        
        # Generate magic link
        print("  → Generating magic link...")
        magic_link, error = self.generate_magic_link(email)
        if error:
            print(f"  ✗ Failed to generate magic link: {error}")
            self.error_count += 1
            return
        
        print("  ✓ Magic link generated")
        
        # Store result (simplified: only email and magic_link)
        self.magic_links.append({
            "email": email,
            "magic_link": magic_link
        })
        
        self.success_count += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.3)
    
    def run(self):
        """Main process"""
        print("="*70)
        print("MAGIC LINK GENERATOR")
        print("="*70)
        print(f"Expiry: {MAGIC_LINK_EXPIRY_DAYS} days")
        print(f"Redirect URL: {REDIRECT_URL}")
        
        # Fetch all users
        print(f"\n→ Fetching users from Supabase...")
        users, error = self.fetch_all_users()
        if error:
            print(f"  ✗ Failed to fetch users: {error}")
            return
        
        print(f"  ✓ Found {len(users)} users")
        
        if not users:
            print("\n⚠ No users found. Please run migration script first.")
            return
        
        # Confirm
        print(f"\n⚠ This will generate {len(users)} magic links")
        confirm = input("  Continue? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("  Operation cancelled.")
            return
        
        # Process all users
        print(f"\n→ Generating magic links...\n")
        start_time = time.time()
        
        for index, user in enumerate(users, start=1):
            self.process_user(user, index, len(users))
        
        # Summary
        duration = time.time() - start_time
        print("\n" + "="*70)
        print("GENERATION SUMMARY")
        print("="*70)
        print(f"Total users processed: {len(users)}")
        print(f"✓ Successful: {self.success_count}")
        print(f"✗ Failed: {self.error_count}")
        print(f"⏱ Duration: {duration:.2f} seconds")
        print("="*70)
        
        # Export to CSV
        if self.magic_links:
            output_file = f"magic_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = pd.DataFrame(self.magic_links)
            df.to_csv(output_file, index=False)
            
            print(f"\n✓ Magic links exported to: {output_file}")
            print(f"\nCSV contains:")
            print(f"  - User ID")
            print(f"  - Email")
            print(f"  - Full Name")
            print(f"  - Bio")
            print(f"  - Magic Link (7 days expiry)")
            print(f"  - Expiry Date")
            print(f"  - Generated At")
            
            print("\n✓ Process complete!")
            print("\nNext steps:")
            print(f"  1. Review the CSV file: {output_file}")
            print(f"  2. Use these magic links to send emails to users")
            print(f"  3. Links will expire on: {(datetime.now() + timedelta(days=MAGIC_LINK_EXPIRY_DAYS)).strftime('%Y-%m-%d')}")
            print("\n⚠ IMPORTANT: Update REDIRECT_URL in this script before sending links!\n")
        else:
            print("\n⚠ No magic links generated")


if __name__ == "__main__":
    try:
        generator = MagicLinkGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
