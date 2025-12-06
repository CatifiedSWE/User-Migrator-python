#!/usr/bin/env python3
"""
Connection Test Script

Tests Supabase connection and validates data before migration.
Run this BEFORE running the actual migration scripts.

Usage:
  python 00_test_connection.py
"""

import os
import sys
import pandas as pd
from supabase import create_client

# Supabase Configuration
SUPABASE_URL = "https://kvidydsfnnrathhpuxye.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt2aWR5ZHNmbm5yYXRoaHB1eHllIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzYxMjc1OCwiZXhwIjoyMDc5MTg4NzU4fQ.oDbAaN2hrEQni0VW8wsKiRqZDbqlnS_Lj-fJ4OsIefo"
EXCEL_FILE = "HeyProData Member Info.xlsx"


def test_connection():
    """Test Supabase connection"""
    print("=" * 70)
    print("SUPABASE CONNECTION TEST")
    print("=" * 70)
    
    try:
        print("\n→ Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("  ✓ Connection successful!")
        
        # Test read access
        print("\n→ Testing database read access...")
        response = supabase.table('user_profiles').select('user_id').limit(1).execute()
        print(f"  ✓ Read access confirmed (found {len(response.data)} existing profiles)")
        
        return supabase, None
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return None, str(e)


def test_excel_file():
    """Test Excel file reading"""
    print("\n" + "=" * 70)
    print("EXCEL FILE VALIDATION")
    print("=" * 70)
    
    # Check file exists
    print(f"\n→ Checking file: {EXCEL_FILE}")
    if not os.path.exists(EXCEL_FILE):
        print(f"  ✗ File not found!")
        print(f"  Expected location: {os.path.abspath(EXCEL_FILE)}")
        return None
    print(f"  ✓ File found: {os.path.abspath(EXCEL_FILE)}")
    
    # Read Excel
    try:
        print("\n→ Reading Excel file...")
        df = pd.read_excel(EXCEL_FILE, sheet_name='Content')
        print(f"  ✓ File read successfully")
        print(f"  ✓ Total rows: {len(df)}")
        
        # Validate columns
        print("\n→ Validating columns...")
        required_columns = ['Name', 'Tagline', 'Categories', 'Logo', 'URL']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"  ✗ Missing columns: {', '.join(missing_columns)}")
            return None
        
        print(f"  ✓ All required columns present")
        
        # Check data quality
        print("\n→ Analyzing data quality...")
        valid_rows = df.dropna(subset=['Name'])
        print(f"  ✓ Valid rows (with Name): {len(valid_rows)}")
        print(f"  ✓ Rows with Tagline: {len(df.dropna(subset=['Tagline']))}")
        print(f"  ✓ Rows with Categories: {len(df.dropna(subset=['Categories']))}")
        print(f"  ✓ Rows with Logo: {len(df.dropna(subset=['Logo']))}")
        print(f"  ✓ Rows with URL: {len(df.dropna(subset=['URL']))}")
        
        return df
    except Exception as e:
        print(f"  ✗ Failed to read file: {e}")
        return None


def preview_migration(df):
    """Preview what will be migrated"""
    print("\n" + "=" * 70)
    print("MIGRATION PREVIEW (First 5 Users)")
    print("=" * 70)
    
    for index, row in df.head(5).iterrows():
        name = row.get('Name', 'N/A')
        tagline = row.get('Tagline', 'N/A')
        categories = row.get('Categories', 'N/A')
        logo = row.get('Logo', 'N/A')
        url = row.get('URL', 'N/A')
        
        # Split name
        name_parts = str(name).strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else "Unknown"
        surname = name_parts[1] if len(name_parts) > 1 else ""
        
        # Parse categories
        roles = [r.strip() for r in str(categories).split(',')] if pd.notna(categories) else []
        
        # Generate email
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', str(name).lower())
        email = f"{clean_name}_{index+1}@heypro.migration"
        
        print(f"\n[{index+1}] {name}")
        print(f"  Email (generated): {email}")
        print(f"  First Name: {first_name}")
        print(f"  Surname: {surname}")
        print(f"  Bio: {tagline[:50]}..." if pd.notna(tagline) and len(str(tagline)) > 50 else f"  Bio: {tagline}")
        print(f"  Roles: {', '.join(roles[:3])}..." if len(roles) > 3 else f"  Roles: {', '.join(roles)}")
        print(f"  Profile Photo: {'✓' if pd.notna(logo) else '✗'}")
        print(f"  Link: {'✓' if pd.notna(url) else '✗'}")


def check_existing_users(supabase):
    """Check for existing users"""
    print("\n" + "=" * 70)
    print("EXISTING USERS CHECK")
    print("=" * 70)
    
    try:
        print("\n→ Checking existing users in Supabase...")
        
        # Check auth.users (via profiles)
        profiles = supabase.table('user_profiles').select('user_id, first_name, surname').execute()
        print(f"  ✓ Found {len(profiles.data)} existing users")
        
        if profiles.data:
            print("\n  Existing users (first 5):")
            for p in profiles.data[:5]:
                print(f"    - {p.get('first_name', '')} {p.get('surname', '')} (ID: {p.get('user_id', '')})")
            
            print("\n  ⚠️ WARNING: Running migration will attempt to create new users.")
            print("     If emails match, migration will fail for those users.")
        else:
            print("\n  ✓ No existing users found. Safe to proceed with migration.")
        
    except Exception as e:
        print(f"  ✗ Failed to check existing users: {e}")


def main():
    """Run all tests"""
    print("\n🔍 PRE-MIGRATION VALIDATION\n")
    
    # Test 1: Supabase Connection
    supabase, error = test_connection()
    if error:
        print("\n❌ FAILED: Cannot connect to Supabase")
        print("   Fix the connection issue before proceeding.")
        sys.exit(1)
    
    # Test 2: Excel File
    df = test_excel_file()
    if df is None:
        print("\n❌ FAILED: Cannot read Excel file")
        print("   Fix the file issue before proceeding.")
        sys.exit(1)
    
    # Test 3: Preview
    preview_migration(df)
    
    # Test 4: Check existing users
    check_existing_users(supabase)
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print("\n✅ All checks passed!")
    print(f"\n📊 Ready to migrate {len(df)} users")
    print("\nNext steps:")
    print("  1. Review the preview above")
    print("  2. Run: python3 01_migrate_users.py")
    print("  3. Run: python3 02_generate_magic_links.py")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
