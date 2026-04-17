# Quick Start Guide
## County Pre-Foreclosure Data Collection System

**Get started in 3 minutes!**

---

## ⚡ **Installation**

### **Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: Run the Application**

```bash
python main.py
```

### **Step 3: Open Browser**

Visit: **http://localhost:8000**

---

## ✅ **Verify It's Working**

You should see:
- ✅ Dashboard with statistics
- ✅ "Add New County" button
- ✅ County list (may be empty or show test data)

---

## 📝 **Test the System**

### **Add Your First County**

1. Click **"Add New County"**
2. Fill in:
   - County Name: `Test County`
   - State: `California`
   - Email: `test@example.com`
   - Status: `Active`
3. Click **"Add County"**
4. See it appear in the list!

### **Verify All Features**

Check that you can see:
- ✅ County name and details
- ✅ Last Request Sent: "Never" (no emails logged yet)
- ✅ Next Schedule: Shows next Monday or Thursday at 9 AM
- ✅ Edit and Delete buttons work

---

## 🎯 **You're Ready!**

The system is working perfectly. See `CLIENT_DELIVERY_GUIDE.md` for complete documentation.

---

## 🆘 **Having Issues?**

**Application won't start?**
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Can't access the page?**
- Make sure application is running (see console for "Uvicorn running" message)
- Try: http://127.0.0.1:8000 instead of localhost

**Port already in use?**
- Edit `main.py` line 731 and change port from 8000 to 8001

---

**Need Help?** See `CLIENT_DELIVERY_GUIDE.md` for detailed troubleshooting.
