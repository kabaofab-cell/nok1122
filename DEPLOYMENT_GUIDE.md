# 🚀 GitHub Preview Deployments Setup Guide

นี่คือคู่มือการตั้ง GitHub Preview Deployments สำหรับโปรเจค nokkub.com

## 📋 ขั้นตอนการตั้ง

### Step 1: ตั้ง Cloudflare API Token

1. ไปที่ [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)
2. สร้าง API Token ใหม่:
   - Click "Create Token"
   - Select "Edit Cloudflare Workers" template หรือสร้างจาก scratch
   - ให้สิทธิ์: `Cloudflare Pages:Edit`, `Account Resources:Edit`, `Workers:Edit`
   - ตั้ง Account Resources เป็น `Include: All accounts`
   - Create token และ copy

### Step 2: ตั้ง GitHub Secrets

1. ไปที่ GitHub Repository: `kabaofab-cell/nok1122`
2. Settings → Secrets and variables → Actions
3. สร้าง 3 secrets นี้:

```
CLOUDFLARE_API_TOKEN = <token จาก step 1>
CLOUDFLARE_ACCOUNT_ID = <account ID ของคุณ>
CLOUDFLARE_PROJECT_NAME = nokkub  (หรือชื่ออื่นที่ต้องการ)
```

**หาค่าเหล่านี้ได้จาก:**
- Account ID: Cloudflare Dashboard → Account → Account ID
- Project Name: ชื่อโปรเจค Cloudflare Pages ของคุณ

### Step 3: ตั้ง Cloudflare Pages

1. ไปที่ [Cloudflare Pages](https://pages.cloudflare.com/)
2. Click "Create a project"
3. เชื่อม GitHub:
   - Select `kabaofab-cell/nok1122`
   - ตั้ง Production branch: `main`
   - ตั้ง Preview deployments: ทุก PR (default)

4. Build Settings:
   - Framework: None
   - Build command: `pip install -r requirements.txt && streamlit run app.py --logger.level=error`
   - Build output directory: (ปล่อยว่าง)
   - Environment variables:
     ```
     STREAMLIT_SERVER_PORT = 8080
     STREAMLIT_SERVER_HEADLESS = true
     ```

5. Save and deploy

### Step 4: ตั้ง Environment Variables (ถ้าจำเป็น)

สำหรับ Google Sheets credentials หรือ API keys:

1. ไปที่ Cloudflare Pages Project Settings
2. Environment → Production/Preview
3. เพิ่ม environment variables ต่อไปนี้:
   - `STREAMLIT_GSHEETS_API_KEY` (ถ้ามี)
   - `STREAMLIT_GSHEETS_WORKSHEET_ID` (ถ้ามี)
   - อื่น ๆ ตามที่ app ต้องการ

## 🧪 การทดสอบ

### ทดสอบ Preview Deployment

```bash
# 1. สร้าง feature branch
git checkout -b feature/test-preview

# 2. ทำการแก้ไขบางอย่าง
# ... แก้ไข files

# 3. Commit & Push
git add .
git commit -m "Test preview deployment"
git push origin feature/test-preview

# 4. สร้าง Pull Request บน GitHub
# GitHub Actions จะสร้าง preview URL อัตโนมัติ

# 5. ทดสอบ preview URL ที่ comment บน PR
```

### ทดสอบ Production Deployment

```bash
# เมื่อพร้อม merge ไป main
git checkout main
git merge feature/test-preview
git push origin main

# Production deployment จะเริ่มอัตโนมัติ
```

## 📊 Workflow Structure

### Files created:

```
.github/workflows/
  ├── preview-deploy.yml    → Deploy ไป preview แต่ละ PR
  ├── production-deploy.yml → Deploy ไป production (main)
  └── ci.yml               → Validate Python syntax (existing)

.streamlit/
  └── config.toml          → Streamlit configuration

Dockerfile                  → Container image for Cloudflare
runtime.txt                 → Python version specification
wrangler.toml              → Cloudflare CLI config
```

### Updated files:

```
app.py                      → เพิ่ม environment detection + preview warning
```

## 🎯 URL Pattern

- **Preview**: `https://pr-{number}.{project-name}.pages.dev`
  - Example: `https://pr-42.nokkub.pages.dev`
  
- **Production**: `https://{project-name}.pages.dev` หรือ custom domain
  - Example: `https://nokkub.pages.dev` หรือ `https://nokkub.com`

## 🔍 Monitoring & Troubleshooting

### ดูสถานะ Workflow

1. GitHub → Actions tab
2. เลือก workflow ที่ต้องการ
3. ดูเป็นทีละ step

### ทั่วไปปัญหา

| ปัญหา | สาเหตุ | วิธีแก้ |
|------|--------|--------|
| "API Token invalid" | Token หมดอายุ หรือผิด | สร้าง token ใหม่ใน Cloudflare |
| Build timeout | Dependencies เยอะ | ปรับ build command หรือ optimize |
| Preview URL 404 | Deployment ไม่เสร็จ | รอ workflow จบ ดูใน Actions logs |
| Google Sheets access denied | Credentials หายไป | ตั้ง STREAMLIT_GSHEETS_API_KEY |

## 📚 Reference

- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Streamlit Deployment](https://docs.streamlit.io/deploy)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)

## ✨ ถัดไป

1. ✅ ตั้ง Cloudflare API Token
2. ✅ ตั้ง GitHub Secrets
3. ✅ ตั้ง Cloudflare Pages Project
4. ✅ ทดสอบ Preview Deployment
5. ✅ ทดสอบ Production Deployment
6. ✅ Monitor deployments

---

**ติดตามความคืบหน้า:** ดู Actions tab ใน GitHub เพื่อติดตามสถานะ workflow
