# User Migration Scripts

These scripts migrate users from HeyProData Excel file to Supabase and generate magic links for authentication.

## 📋 Prerequisites

### 1. Install Dependencies
```bash
pip install supabase pandas openpyxl
```

### 2. Prepare Data
- Place `data spreadsheet.xlsx` in the same directory as the scripts
- Ensure the Excel file has columns:
  - Name
  - URL (optional)
  - Tagline (becomes Bio)
  - Categories (becomes Roles)
  - Logo (becomes Profile Photo)
  - Email (real email addresses)

### 3. Configure Supabase
The scripts are pre-configured with your Supabase credentials:
- URL: `https://kvidydsfnnrathhpuxye.supabase.co`
- Service Key: Already embedded (keep secure!)

## 🚀 Usage

### Script 1: Migrate Users

**Purpose:** Creates users in Supabase from the Excel file

```bash
python 01_migrate_users.py
```

**What it does:**
1. Reads users from Excel file
2. Creates auth.users entries with real emails from Email column
3. Creates user_profiles with:
   - Name (split into first_name and surname)
   - Bio (from Tagline)
   - Profile Photo URL (from Logo)
4. Creates user_roles from Categories
5. Creates user_links from URL field
6. Generates migration log CSV

**Output:**
- Console log with progress
- `migration_log_YYYYMMDD_HHMMSS.csv` - detailed migration report

**Email Handling:**
The script uses real emails from the "Email" column in the Excel file.
If an email is missing, it will generate one as fallback:
- Format: `{sanitized_name}_{index}@heypro.migration`
- Example: `tinageorge_1@heypro.migration`

### Script 2: Generate Magic Links

**Purpose:** Generates magic links for all migrated users (7 days expiry)

```bash
python 02_generate_magic_links.py
```

**What it does:**
1. Fetches all users from Supabase
2. Generates magic links using Supabase Admin API
3. Sets 7-day expiration
4. Exports simplified CSV with magic links

**Output:**
- `magic_links_YYYYMMDD_HHMMSS.csv` containing:
  - email
  - magic_link (clickable authentication link)

**⚠️ IMPORTANT:** Before running this script:
1. Update `REDIRECT_URL` in the script to your actual domain
2. Example: `https://yourdomain.com/auth/callback`

## 📊 Data Mapping

| Excel Column | Supabase Table | Field | Notes |
|--------------|----------------|-------|-------|
| Name | user_profiles | first_name, surname | Split by space |
| Tagline | user_profiles | bio | Direct mapping |
| Categories | user_roles | role_name | Split by comma, multiple roles |
| Logo | user_profiles | profile_photo_url | Direct URL |
| URL | user_links | url | Saved as "Profile Link" |
| Email | auth.users | email | Real email addresses |

## 🔐 Security Notes

1. **Service Key:** The Supabase service key is embedded in the scripts. Keep these files secure!
2. **Magic Links:** Valid for 7 days only. Users must use them within this period.
3. **Email Confirmation:** Users are auto-confirmed (no OTP required)

## 📝 Example Workflow

### Step 1: Migrate Users
```bash
$ python 01_migrate_users.py

======================================================================
USER MIGRATION: HeyProData → Supabase
======================================================================

→ Reading Excel file: HeyProData Member Info.xlsx
  ✓ Found 70 users to migrate
  ✓ 70 valid users after filtering

⚠ WARNING: This will create 70 new users in Supabase
  Continue? (yes/no): yes

→ Starting migration...

[1] Migrating: Tina George (tinageorge_1@heypro.migration)
  → Creating auth user...
  ✓ Auth user created: 550e8400-e29b-41d4-a716-446655440000
  → Creating user profile...
  ✓ User profile created
  → Creating 5 roles...
  ✓ Roles created: Producer, Producer | Creative, Production Manager, ...
  → Creating user link...
  ✓ User link created
  ✓ Migration complete

...

======================================================================
MIGRATION SUMMARY
======================================================================
Total users processed: 70
✓ Successful: 68
✗ Failed: 2
⏱ Duration: 45.23 seconds
======================================================================

→ Migration log saved: migration_log_20250119_143022.csv

✓ Migration complete!

Next steps:
  1. Run script 02_generate_magic_links.py to generate magic links
  2. Send magic links to users via email
```

### Step 2: Generate Magic Links
```bash
$ python 02_generate_magic_links.py

======================================================================
MAGIC LINK GENERATOR
======================================================================
Expiry: 7 days
Redirect URL: https://yourdomain.com/auth/callback

→ Fetching users from Supabase...
  ✓ Found 68 users

⚠ This will generate 68 magic links
  Continue? (yes/no): yes

→ Generating magic links...

[1/68] Processing: Tina George
  → Fetching email...
  ✓ Email: tinageorge_1@heypro.migration
  → Generating magic link...
  ✓ Magic link generated

...

======================================================================
GENERATION SUMMARY
======================================================================
Total users processed: 68
✓ Successful: 68
✗ Failed: 0
⏱ Duration: 28.45 seconds
======================================================================

✓ Magic links exported to: magic_links_20250119_143525.csv

CSV contains:
  - User ID
  - Email
  - Full Name
  - Bio
  - Magic Link (7 days expiry)
  - Expiry Date
  - Generated At

✓ Process complete!

Next steps:
  1. Review the CSV file: magic_links_20250119_143525.csv
  2. Use these magic links to send emails to users
  3. Links will expire on: 2025-01-26

⚠ IMPORTANT: Update REDIRECT_URL in this script before sending links!
```

## 🛠️ Troubleshooting

### Issue: "Excel file not found"
**Solution:** Ensure `HeyProData Member Info.xlsx` is in the same directory as the scripts

### Issue: "Failed to create auth user"
**Possible causes:**
- Email already exists in Supabase
- Rate limiting (the script has 0.5s delay between users)
- Invalid Supabase credentials

### Issue: "Failed to generate magic link"
**Possible causes:**
- User doesn't exist in auth.users
- Invalid email format
- Supabase API rate limiting

### Issue: "Module not found: supabase"
**Solution:**
```bash
pip install supabase pandas openpyxl
```

## 📧 Sending Magic Links (Not Included)

These scripts generate the CSV with magic links but **do not send emails**.

To send emails to users, you can:
1. Use the generated CSV with your email service (SendGrid, Mailgun, etc.)
2. Create a custom email script using the CSV
3. Manually send emails (for small batches)

**Example email template:**
```
Subject: Welcome to [Your Platform] - Complete Your Migration

Hi {first_name},

We've migrated your HeyProData account to our new platform.

Click the link below to access your account (valid for 7 days):
{magic_link}

Your profile includes:
- Name: {full_name}
- Bio: {bio}

Welcome aboard!

Best regards,
[Your Team]
```

## 🔄 Re-running Scripts

### Re-run Migration Script
**⚠️ WARNING:** This will attempt to create duplicate users and will fail due to unique email constraints.

**To re-run:**
1. Delete users from Supabase first (use Supabase Dashboard)
2. OR modify the script to skip existing users

### Re-run Magic Link Generator
**✓ SAFE:** You can run this multiple times. It will generate fresh magic links each time.

## 📊 Output Files

### migration_log_YYYYMMDD_HHMMSS.csv
```csv
index,name,email,status,user_id,error
1,Tina George,heyprodata@gmail.com,success,550e8400-...,
2,Rajj M Rao,raaj.rao.01@gmail.com,success,661f9511-...,
3,Gen AI,iamtinageorge@gmail.com,failed,,Auth creation failed: email already exists
```

### magic_links_YYYYMMDD_HHMMSS.csv
```csv
email,magic_link
heyprodata@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...
raaj.rao.01@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...
```

## 🎯 Success Indicators

✅ **Migration Successful:**
- All users created in auth.users
- All profiles created in user_profiles
- Roles and links populated
- Log file shows "success" status

✅ **Magic Links Generated:**
- CSV file created with all users
- All magic_link fields populated
- Links start with: `https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...`
- Expiry date is 7 days from generation

## 💡 Tips

1. **Test First:** Run migration on a few users first (edit the Excel file)
2. **Backup:** Keep the original Excel file safe
3. **Monitor:** Check Supabase Dashboard to verify users are created
4. **Logs:** Review log files for any errors or warnings
5. **Rate Limits:** Scripts have built-in delays to avoid rate limiting

## 🆘 Support

If you encounter issues:
1. Check the error message in console output
2. Review the log CSV files
3. Verify Supabase credentials are correct
4. Check Supabase Dashboard for actual data
5. Ensure Excel file structure matches expected format

---

**Created:** January 2025
**Version:** 1.0
**Purpose:** HeyProData to Supabase Migration
