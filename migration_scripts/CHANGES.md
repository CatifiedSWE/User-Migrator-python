# Migration Scripts - Recent Changes

## 📋 Summary

Updated the migration scripts to use **real email addresses** from the new Excel file instead of generating dummy emails.

---

## 🔄 What Changed

### 1. **New Excel File**
- **Old:** `HeyProData_Member_Info.xlsx`
- **New:** `data spreadsheet.xlsx` ✅
- **Location:** `/app/migration_scripts/`

### 2. **Email Handling**
- **Old:** Generated emails like `tinageorge_1@heypro.migration`
- **New:** Uses real emails from "Email" column (e.g., `heyprodata@gmail.com`) ✅
- **Fallback:** If email is missing, still generates dummy email

### 3. **Magic Links CSV Output**
- **Old:** CSV with 9 columns (user_id, email, first_name, surname, full_name, bio, magic_link, expiry_date, generated_at)
- **New:** Simplified CSV with only 2 columns:
  - `email`
  - `magic_link` ✅

---

## 📊 Data Mapping (Updated)

| Excel Column | Supabase Table | Field | Change |
|--------------|----------------|-------|--------|
| Name | user_profiles | first_name, surname | No change |
| Tagline | user_profiles | bio | No change |
| Categories | user_roles | role_name | No change |
| Logo | user_profiles | profile_photo_url | No change |
| URL | user_links | url | No change |
| **Email** | auth.users | **email** | ✅ **NEW** - Real emails |

---

## 📁 Files Modified

1. ✅ `/app/migration_scripts/01_migrate_users.py`
   - Changed `EXCEL_FILE` to `"data spreadsheet.xlsx"`
   - Updated email extraction to use "Email" column
   - Added fallback for missing emails

2. ✅ `/app/migration_scripts/02_generate_magic_links.py`
   - Simplified CSV output to only `email` and `magic_link`

3. ✅ `/app/migration_scripts/README.md`
   - Updated documentation to reflect new file and email handling

4. ✅ `/app/migration_scripts/DATA_MAPPING.md`
   - Updated all references from "Featured" to "Email"
   - Updated example outputs

5. ✅ `/app/migration_scripts/QUICK_START.md`
   - Updated file references and examples

---

## 🧪 Verification

### Test Results
```
✅ Excel file readable: 70 users found
✅ Email column exists
✅ Email extraction working: 68/70 users have emails
✅ 2 users will get fallback generated emails
```

### Sample Data
```
Tina George  → heyprodata@gmail.com
Rajj M Rao   → raaj.rao.01@gmail.com
Gen AI       → iamtinageorge@gmail.com
```

---

## 🚀 How to Use

### Step 1: Run Migration
```bash
cd /app/migration_scripts
python3 01_migrate_users.py
```

**Output:**
- Creates users with real emails in Supabase
- Generates `migration_log_YYYYMMDD_HHMMSS.csv`

### Step 2: Generate Magic Links
```bash
python3 02_generate_magic_links.py
```

**Output:**
- Generates `magic_links_YYYYMMDD_HHMMSS.csv` with format:
  ```csv
  email,magic_link
  heyprodata@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...
  raaj.rao.01@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...
  ```

---

## 💡 Key Improvements

1. **Real Emails**: No more dummy emails - users get real email addresses ✅
2. **Simplified Output**: Magic links CSV is cleaner with only essential columns ✅
3. **Better UX**: Easier to send magic links to users via email ✅
4. **Flexible**: Auto-falls back to generated emails if real email is missing ✅

---

## 📝 Example CSV Outputs

### Migration Log
```csv
index,name,email,status,user_id,error
1,Tina George,heyprodata@gmail.com,success,550e8400-...,
2,Rajj M Rao,raaj.rao.01@gmail.com,success,661f9511-...,
```

### Magic Links (NEW FORMAT)
```csv
email,magic_link
heyprodata@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=abc123...
raaj.rao.01@gmail.com,https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=def456...
```

---

## ⚠️ Important Notes

1. **Email Column**: The script now looks for the "Email" column in the Excel file
2. **Sheet Name**: Works with both "Content" sheet and first sheet (Sheet1)
3. **68 out of 70 users** have real email addresses
4. **2 users** will get generated emails as fallback
5. **Magic links expire** in 7 days

---

## ✅ Ready to Use

The migration scripts are now updated and ready to use with the new Excel file containing real email addresses!

**Last Updated:** December 2024
**Status:** ✅ Production Ready
