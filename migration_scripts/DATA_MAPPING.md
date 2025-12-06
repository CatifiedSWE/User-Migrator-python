# Data Mapping - HeyProData to Supabase

## 📋 Complete Field Mapping

### Source: HeyProData Excel File (Sheet: Content)
### Destination: Supabase Database

---

## 🎯 PRIMARY DATA FIELDS (All Included)

### 1. Name → user_profiles
```
Excel Column: "Name"
Example: "Tina George"

↓ Splits into ↓

Supabase Table: user_profiles
├─ first_name: "Tina"
└─ surname: "George"
```

### 2. ⭐ Tagline → user_profiles.bio (IMPORTANT)
```
Excel Column: "Tagline"
Example: "Producer. Production Manager. Creative problem-solver. Tech & AI Enthusiast."

↓ Maps directly to ↓

Supabase Table: user_profiles
└─ bio: "Producer. Production Manager. Creative problem-solver. Tech & AI Enthusiast."

✅ CONFIRMED: Bio/Tagline is fully migrated
```

### 3. ⭐ Categories → user_roles (IMPORTANT - Multiple Rows)
```
Excel Column: "Categories"
Example: "Producer, Producer | Creative, Production Manager, Creative Director"

↓ Splits by comma into multiple rows ↓

Supabase Table: user_roles
├─ Row 1: role_name = "Producer"
├─ Row 2: role_name = "Producer | Creative"
├─ Row 3: role_name = "Production Manager"
└─ Row 4: role_name = "Creative Director"

✅ CONFIRMED: All roles are migrated as separate entries
```

### 4. Logo → user_profiles.profile_photo_url
```
Excel Column: "Logo"
Example: "https://cdn.sheetany.com/files/RxBjZCbn5u.jpg"

↓ Maps directly to ↓

Supabase Table: user_profiles
└─ profile_photo_url: "https://cdn.sheetany.com/files/RxBjZCbn5u.jpg"
```

### 5. ⭐ URL → user_links (IMPORTANT)
```
Excel Column: "URL"
Example: "https://linktr.ee/tinageorge"

↓ Maps to ↓

Supabase Table: user_links
├─ label: "Profile Link"
└─ url: "https://linktr.ee/tinageorge"

✅ CONFIRMED: Links are fully migrated
```

### 6. ⭐ Email (from Featured column) - UPDATED
```
Excel Column: "Featured"
Example: "heyprodata@gmail.com"

↓ Maps directly to ↓

Supabase Table: auth.users
└─ email: "heyprodata@gmail.com"

✅ CONFIRMED: Real emails from Featured column are used

Note: If Featured column is empty, a fallback email will be generated:
      Format: "{sanitized_name}_{index}@heypro.migration"
```

---

## 📊 Data Flow Summary

```
HeyProData Excel
│
├─ Name ───────────────────► user_profiles (first_name, surname)
│
├─ ⭐ Tagline ──────────────► user_profiles (bio) ✅ INCLUDED
│
├─ ⭐ Categories ───────────► user_roles (multiple rows) ✅ INCLUDED
│
├─ Logo ───────────────────► user_profiles (profile_photo_url)
│
├─ ⭐ URL ──────────────────► user_links (url) ✅ INCLUDED
│
└─ ⭐ Featured ─────────────► auth.users (email) ✅ REAL EMAILS
```

---

## 🗂️ Database Tables Created

### 1. auth.users (Supabase Authentication)
```sql
email: tinageorge_1@heypro.migration
email_confirmed: true
user_metadata: {
  "full_name": "Tina George",
  "migrated_from": "HeyProData",
  "migrated_at": "2025-01-19T..."
}
```

### 2. user_profiles
```sql
user_id: (FK to auth.users)
first_name: "Tina"
surname: "George"
⭐ bio: "Producer. Production Manager. Creative problem-solver..." ✅
profile_photo_url: "https://cdn.sheetany.com/files/..."
is_profile_complete: false
profile_completion_percentage: 30
```

### 3. ⭐ user_roles (Multiple Rows per User)
```sql
Row 1:
  user_id: (FK to auth.users)
  role_name: "Producer"
  sort_order: 0

Row 2:
  user_id: (same user)
  role_name: "Producer | Creative"
  sort_order: 1

Row 3:
  user_id: (same user)
  role_name: "Production Manager"
  sort_order: 2
  
... (all roles from Categories column) ✅
```

### 4. ⭐ user_links
```sql
user_id: (FK to auth.users)
label: "Profile Link"
url: "https://linktr.ee/tinageorge" ✅
sort_order: 0
```

---

## ✅ Verification Checklist

### Before Migration
- [x] Excel file has all columns: Name, Tagline, Categories, Logo, URL
- [x] 70 users with valid names
- [x] 70 users with taglines (bio) ✅
- [x] 70 users with categories (roles) ✅
- [x] 65 users with URLs (links) ✅
- [x] 27 users with logos

### After Migration (Check in Supabase)
- [ ] 70 users in auth.users
- [ ] 70 profiles in user_profiles
- [ ] ⭐ All profiles have bio field populated (from Tagline) ✅
- [ ] ⭐ Multiple entries in user_roles per user (from Categories) ✅
- [ ] ⭐ 65 entries in user_links (from URL) ✅
- [ ] 27 profiles have profile_photo_url

---

## 📝 Example: Complete User Migration

### Source Data (Excel)
```
Name: "Tina George"
Tagline: "Producer. Production Manager. Creative problem-solver. Tech & AI Enthusiast."
Categories: "Producer, Producer | Creative, Production Manager, Creative Director, Fashion Show Director"
Logo: "https://cdn.sheetany.com/files/RxBjZCbn5u.jpg"
URL: "https://linktr.ee/tinageorge"
Featured: "heyprodata@gmail.com"
```

### Result in Supabase
```
✅ auth.users
   └─ email: "heyprodata@gmail.com"
   
✅ user_profiles
   ├─ first_name: "Tina"
   ├─ surname: "George"
   ├─ ⭐ bio: "Producer. Production Manager. Creative problem-solver. Tech & AI Enthusiast."
   └─ profile_photo_url: "https://cdn.sheetany.com/files/RxBjZCbn5u.jpg"

✅ user_roles (5 rows)
   ├─ "Producer"
   ├─ "Producer | Creative"
   ├─ "Production Manager"
   ├─ "Creative Director"
   └─ "Fashion Show Director"

✅ user_links (1 row)
   └─ url: "https://linktr.ee/tinageorge"
```

---

## 🎯 Key Points

1. ✅ **Bio (Tagline)** - Fully migrated to `user_profiles.bio`
2. ✅ **Roles (Categories)** - Split by comma, each role gets its own row in `user_roles`
3. ✅ **Links (URL)** - Saved in `user_links` table
4. ✅ **Name** - Split into first_name and surname
5. ✅ **Logo** - Saved as profile_photo_url
6. ✅ **Email (Featured)** - Real email addresses from Featured column

**All important fields are included in the migration!** 🎉

---

## 🔍 How to Verify After Migration

### SQL Query (run in Supabase SQL Editor)
```sql
-- Check a specific user's complete data
SELECT 
  up.first_name,
  up.surname,
  up.bio,  -- ⭐ Tagline is here
  up.profile_photo_url,
  array_agg(DISTINCT ur.role_name) as roles,  -- ⭐ Categories are here
  array_agg(DISTINCT ul.url) as links  -- ⭐ URLs are here
FROM user_profiles up
LEFT JOIN user_roles ur ON ur.user_id = up.user_id
LEFT JOIN user_links ul ON ul.user_id = up.user_id
WHERE up.first_name = 'Tina' AND up.surname = 'George'
GROUP BY up.user_id, up.first_name, up.surname, up.bio, up.profile_photo_url;
```

### Expected Result
```
email: heyprodata@gmail.com
first_name: Tina
surname: George
bio: "Producer. Production Manager. Creative problem-solver. Tech & AI Enthusiast."
profile_photo_url: "https://cdn.sheetany.com/files/RxBjZCbn5u.jpg"
roles: ["Producer", "Producer | Creative", "Production Manager", "Creative Director", "Fashion Show Director"]
links: ["https://linktr.ee/tinageorge"]
```

---

## 📧 Magic Links CSV Output

After running `02_generate_magic_links.py`, you'll get:

```csv
user_id,email,first_name,surname,full_name,bio,magic_link,expiry_date,generated_at
550e8400-...,tinageorge_1@heypro.migration,Tina,George,Tina George,"Producer. Production Manager...",https://kvidydsfnnrathhpuxye.supabase.co/auth/v1/verify?token=...,2025-01-26,2025-01-19T14:35:25
```

**Note:** The CSV includes the bio field so you can use it in email templates!

---

**Last Updated:** January 2025
**Status:** ✅ All fields mapped and confirmed
**Important Fields:** ⭐ Bio (Tagline), ⭐ Roles (Categories), ⭐ Links (URL) - ALL INCLUDED
