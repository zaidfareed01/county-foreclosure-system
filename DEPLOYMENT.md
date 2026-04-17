# Deployment Guide - Render.com

## 🚀 Deploy County Pre-Foreclosure System to Render.com

This guide will walk you through deploying your application to Render.com with PostgreSQL database.

---

## ✅ Prerequisites

- [x] GitHub account
- [x] Render.com account (free - no credit card required)
- [x] Code pushed to GitHub repository

---

## 📋 Step-by-Step Deployment

### **Step 1: Push Code to GitHub**

If you haven't already, push your code to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render.com deployment"

# Create GitHub repository at github.com/new

# Add remote (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin master
```

---

### **Step 2: Sign Up for Render.com**

1. Go to https://render.com/
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest option)
4. Authorize Render to access your repositories

---

### **Step 3: Deploy Using Blueprint (Automatic)**

Render will automatically detect your `render.yaml` file and set everything up!

1. **Go to Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → Select **"Blueprint"**
3. **Connect Repository**:
   - Click "Connect" next to your repository
   - If not listed, click "Configure account" to grant access
4. **Review Blueprint**:
   - Service name: `county-foreclosure-api`
   - Database name: `county-foreclosure-db`
   - Click **"Apply"**
5. **Wait for Deployment** (5-10 minutes):
   - Backend service will build
   - PostgreSQL database will be created
   - Tables will be auto-created on first run

---

### **Step 4: Verify Deployment**

Once deployment completes:

1. **Get Your URL**:
   - Look for: `https://county-foreclosure-api.onrender.com`

2. **Test API**:
   ```
   https://county-foreclosure-api.onrender.com/api
   ```
   Should return:
   ```json
   {
     "message": "County Pre-Foreclosure System API",
     "version": "1.0.0",
     "status": "running"
   }
   ```

3. **Test Frontend**:
   ```
   https://county-foreclosure-api.onrender.com/
   ```
   Should show your React app!

4. **Add a County**:
   - Click "Add New County"
   - Fill in form
   - Submit
   - Refresh page - county should persist! ✅

---

## 🔧 Manual Setup (Alternative Method)

If Blueprint doesn't work, deploy manually:

### **A. Create PostgreSQL Database**

1. **Dashboard** → **"New +"** → **"PostgreSQL"**
2. **Fill details**:
   - Name: `county-foreclosure-db`
   - Database: `county_foreclosure`
   - User: `county_user`
   - Region: Oregon (or closest to you)
   - Plan: **Free**
3. **Click "Create Database"**
4. **Wait 2-3 minutes** for database to provision
5. **Copy Internal Database URL** (starts with `postgres://`)

### **B. Create Web Service**

1. **Dashboard** → **"New +"** → **"Web Service"**
2. **Connect Repository**: Select your GitHub repo
3. **Fill details**:
   - Name: `county-foreclosure-api`
   - Region: Oregon
   - Branch: `master`
   - Root Directory: (leave empty)
   - Environment: **Python 3**
   - Build Command: `bash build.sh`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**
4. **Advanced Settings** → **Environment Variables**:
   - Add `DATABASE_URL` = (paste the database URL from step A5)
   - Add `PYTHON_VERSION` = `3.11.6`
   - Add `NODE_VERSION` = `18.18.0`
5. **Click "Create Web Service"**
6. **Wait 10-15 minutes** for build & deploy

---

## ⚡ Important Notes

### **Cold Starts on Free Tier**
- App **sleeps after 15 minutes** of inactivity
- First request after sleep takes **20-60 seconds**
- Subsequent requests are instant

**Solution**: Use UptimeRobot to ping every 10 minutes (free):
1. Go to https://uptimerobot.com/
2. Add monitor: `https://your-app.onrender.com/api`
3. Interval: 5 minutes
4. App stays awake! 🎉

### **Database Expiration**
- Free PostgreSQL expires after **90 days**
- You'll receive email warning
- Simply create new database and restore backup
- Update `DATABASE_URL` in environment variables

---

## 🐛 Troubleshooting

### **Build Fails**

**Error: "bash build.sh: No such file"**
- Solution: Make sure `build.sh` is pushed to GitHub
- Run: `git add build.sh && git commit -m "Add build script" && git push`

**Error: "ModuleNotFoundError: No module named 'psycopg2'"**
- Solution: Check `requirements.txt` contains `psycopg2-binary==2.9.9`

### **Frontend Not Loading**

**Shows: "Frontend not built"**
- Check build logs: Does `yarn build` succeed?
- Make sure `frontend/` folder is in your repo
- Try manual deploy trigger in Render dashboard

### **Database Connection Errors**

**Error: "could not connect to server"**
- Wait 5 minutes - database might still be initializing
- Check `DATABASE_URL` environment variable is set correctly
- Make sure database and web service are in same region

### **CORS Errors in Browser**

**Error: "No 'Access-Control-Allow-Origin' header"**
- This shouldn't happen (CORS is set to `*` in main.py)
- If it does, check Render logs for errors

---

## 📊 Monitoring Your App

### **View Logs**
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. See real-time logs

### **View Database**
1. Go to database in Dashboard
2. Click "Connect"
3. Use connection string with any PostgreSQL client
4. Or use Render's Shell tab

### **Check Metrics**
1. Dashboard → Your service
2. See CPU, Memory, Request count
3. Free tier shows basic metrics

---

## 🔄 Updating Your App

### **Deploy New Changes**

```bash
# Make your code changes
git add .
git commit -m "Update feature X"
git push

# Render automatically deploys! ✅
# Check deploy progress in Dashboard
```

### **Manual Deploy**
1. Dashboard → Your service
2. Click "Manual Deploy" → "Deploy latest commit"

---

## 💾 Database Backup

### **Automatic Backups**
- Not available on free tier
- Upgrade to paid plan for automated backups

### **Manual Backup**
```bash
# Get database connection string from Render Dashboard
# Run this command locally:

pg_dump "postgres://user:password@host/database" > backup.sql

# Restore if needed:
psql "postgres://user:password@host/database" < backup.sql
```

---

## 🎉 You're Live!

Your app is now accessible at:
```
https://county-foreclosure-api.onrender.com
```

Share this URL with anyone - no installation required!

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **This Project Issues**: https://github.com/YOUR_USERNAME/YOUR_REPO/issues

---

## 🚀 Next Steps

1. ✅ Set up UptimeRobot to prevent cold starts
2. ✅ Set up regular database backups
3. ✅ Add custom domain (optional - requires paid plan)
4. ✅ Enable HTTPS (automatic on Render)
5. ✅ Monitor usage and upgrade if needed

---

## 💰 Cost Summary

| Item | Free Tier | Paid Tier |
|------|-----------|-----------|
| Web Service | 750 hours/month | $7/month (always-on) |
| PostgreSQL | 1 GB (90 days) | $7/month (persistent) |
| Bandwidth | 100 GB/month | 1000 GB/month |
| **Total** | **$0/month** | **$14/month** |

**Free tier is perfect for:**
- Personal projects
- Demos
- Portfolio
- Low-traffic apps

**Upgrade when:**
- Need always-on (no cold starts)
- Permanent database
- Heavy traffic
- Production business app

---

Happy deploying! 🎊
