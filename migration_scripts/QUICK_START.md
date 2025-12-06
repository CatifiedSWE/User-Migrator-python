# Quick Start Guide - User Migration

## 🚀 Quick Setup (5 minutes)

### Step 1: Navigate to Scripts Directory
```bash
cd /app/migration_scripts
```

### Step 2: Verify Files
```bash
ls -lah
# You should see:
# - 01_migrate_users.py
# - 02_generate_magic_links.py
# - data spreadsheet.xlsx
# - README.md
```

### Step 3: Test Connection (Optional)
```bash
python3 << 'EOF'
from supabase import create_client
supabase = create_client(
    "https://kvidydsfnnrathhpuxye.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt2aWR5ZHNmbm5yYXRoaHB1eHllIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzYxMjc1OCwiZXhwIjoyMDc5MTg4NzU4fQ.oDbAaN2hrEQni0VW8wsKiRqZDbqlnS_Lj-fJ4OsIefo"
)
print("✓ Supabase connection successful!")
EOF
```

## 📝 Migration Process

### Script 1: Migrate Users (Step 1 of 2)
```bash
cd /app/migration_scripts
python3 01_migrate_users.py
```

**What happens:**
- Reads 70 users from Excel
- Creates auth accounts
- Creates profiles with bio, photo, roles
- Takes ~1 minute
- Generates log file

**Output:**
- `migration_log_YYYYMMDD_HHMMSS.csv`

### Script 2: Generate Magic Links (Step 2 of 2)
```bash
cd /app/migration_scripts
python3 02_generate_magic_links.py
```

**⚠️ IMPORTANT:** Before running, update `REDIRECT_URL` in the script:
```python
# Edit line 19 in 02_generate_magic_links.py
REDIRECT_URL = 'https://YOUR_DOMAIN.com/auth/callback'
```

**What happens:**
- Fetches all migrated users
- Generates 7-day magic links
- Exports CSV with links
- Takes ~30 seconds

**Output:**
- `magic_links_YYYYMMDD_HHMMSS.csv`

## 📊 Expected Results

### Migration Log Example
```csv
index,name,email,status,user_id
1,Tina George,heyprodata@gmail.com,success,550e8400-...
2,Rajj M Rao,raaj.rao.01@gmail.com,success,661f9511-...
...
```

### Magic Links CSV Example (Simplified)
```csv
email,magic_link
heyprodata@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...
raaj.rao.01@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...
...
```

## ✅ Verification

### Check Supabase Dashboard
1. Go to: https://supabase.com/dashboard/project/kvidydsfnnrathhpuxye
2. Navigate to: Authentication → Users
3. Verify: 70 users created
4. Navigate to: Table Editor → user_profiles
5. Verify: Profiles with names, bios, photos

### Quick Database Check
```bash
python3 << 'EOF'
from supabase import create_client
supabase = create_client(
    "https://kvidydsfnnrathhpuxye.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt2aWR5ZHNmbm5yYXRoaHB1eHllIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzYxMjc1OCwiZXhwIjoyMDc5MTg4NzU4fQ.oDbAaN2hrEQni0VW8wsKiRqZDbqlnS_Lj-fJ4OsIefo"
)
profiles = supabase.table('user_profiles').select('*').limit(5).execute()
print(f"✓ Found {len(profiles.data)} profiles")
for p in profiles.data:
    print(f"  - {p['first_name']} {p['surname']}")
EOF
```

## 🎯 What Gets Migrated

| Source Data | → | Destination |
|-------------|---|-------------|
| Name | → | first_name + surname (user_profiles) |
| Tagline | → | bio (user_profiles) |
| Logo | → | profile_photo_url (user_profiles) |
| Categories | → | role_name (user_roles, multiple rows) |
| URL | → | url (user_links) |
| (generated) | → | email (auth.users) |

## 🔧 Troubleshooting

### Issue: "Excel file not found"
```bash
# Copy file to correct location
cp /path/to/HeyProData*.xlsx /app/migration_scripts/
```

### Issue: "Module 'supabase' not found"
```bash
pip install supabase pandas openpyxl
```

### Issue: "Failed to create user - email exists"
This means you've already run the migration. To re-run:
1. Delete users from Supabase Dashboard first, OR
2. Modify the script to skip existing users

### Issue: Rate limiting
The scripts have built-in delays (0.5s per user). If you still hit limits:
1. Increase delay in script
2. Run in smaller batches

## 📧 Next Step: Send Emails

After generating magic links, use the CSV to send emails:

**Option 1: Manual (for testing)**
- Open CSV
- Copy magic link
- Send to user's actual email

**Option 2: Automated (recommended)**
- Use SendGrid, Mailgun, or similar
- Import CSV
- Create email template
- Send bulk emails

**Email Template:**
```
Subject: Welcome to [Platform] - Account Migration

Hi {first_name},

Your HeyProData account has been migrated!

Click here to access your account:
{magic_link}

This link expires in 7 days.

Best regards,
The Team
```

## 🔒 Security Reminders

1. ✅ Service keys are already configured
2. ✅ Magic links expire in 7 days
3. ✅ Users are auto-confirmed (no OTP needed)
4. ⚠️ Keep CSV files secure (contain magic links)
5. ⚠️ Don't commit service keys to git

## 📞 Support

For issues:
1. Check console output for errors
2. Review log CSV files
3. Verify Supabase dashboard
4. Check README.md for detailed docs

---

**Ready?** Run the scripts now! 🚀

```bash
cd /app/migration_scripts
python3 01_migrate_users.py
python3 02_generate_magic_links.py
```
