# Railway Deployment Guide for ZipperBot

## ⚠️ Important: Credential Storage Issue

Railway has an **ephemeral filesystem**, which means files are deleted when the bot restarts or redeploys. This affects credential storage!

---

## Issue: User Credentials Won't Persist

### What Happens Now
```
1. User authenticates: /google → code → saves to file
2. Bot uses credentials normally
3. Bot restarts/redeploys → FILES ARE DELETED ❌
4. User gets "not connected" error
5. User must re-authenticate: /google again
```

### The Problem Files
- `google_credentials/user_123456_token.json` - DELETED on restart
- `google_credentials/user_123456_folder.json` - DELETED on restart
- `user_files/` - DELETED on restart

---

## Solutions

### Option 1: Accept Re-authentication (SIMPLE ✅)
**How it works:** Users re-authenticate after bot restarts
- Pros: Simple, no code changes needed
- Cons: Users must send `/google` again after restarts

**This is recommended for most users.**

### Option 2: Use Railway's Postgres (BETTER ✓✓)
**How it works:** Store credentials in Railway's database
- Pros: Persistent, works across restarts
- Cons: Need code changes, need Postgres setup

### Option 3: Use Railway's Disk (BEST ✓✓✓)
**How it works:** Mount a persistent disk
- Pros: No code changes, just configuration
- Cons: Need Railway paid plan, volume configuration

---

## Deployment Steps

### Step 1: Prepare Files ✅ (Already done!)

You need these files:
- ✅ `Procfile` - How to run the bot
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Dependencies
- ✅ `bot.py` - The bot code

All already created! ✨

### Step 2: Set Up Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Create new project
4. Select "Deploy from GitHub repo"
5. Choose your ZipperBot repository
6. Wait for it to link

### Step 3: Add Environment Variables

Railway → Your Project → Variables → Add:

```
TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

**Note:** `client_secrets.json` cannot be stored as environment variable (too large).

### Step 4: Upload client_secrets.json

**Option A: Via GitHub (Recommended)**
1. Add `client_secrets.json` to your repo
2. Add to `.gitignore` temporarily (or not)
3. Push to GitHub
4. Railway pulls automatically

**Option B: Manually (If sensitive)**
1. In Railway dashboard
2. Go to Deployments
3. Use file upload if available
4. Or: Create it manually in Railway shell

### Step 5: Deploy

1. Push to GitHub (if using git)
2. Railway auto-deploys from git
3. Or click "Deploy" manually in Railway dashboard
4. Watch logs for errors

### Step 6: Test

1. Get your Railway bot URL/domain (if applicable)
2. Send `/start` to your Telegram bot
3. Should respond with welcome message ✅

---

## Important Configuration for Railway

### Environment Variables Needed

```
TELEGRAM_BOT_TOKEN=your_bot_token
```

### Files Needed in Repo

```
bot.py
requirements.txt
Procfile              ← REQUIRED
runtime.txt           ← OPTIONAL but good
.gitignore            ← Already present
client_secrets.json   ← Put in repo or upload manually
```

### What NOT to Include in Repo

```
.env                  ← Use Railway variables instead
user_files/           ← Gets created automatically
google_credentials/   ← Gets created automatically
```

---

## Handling the Ephemeral Filesystem

### Current Behavior (Option 1 - Recommended for now)

```
User connects Google: /google
    ↓
Bot saves token to google_credentials/user_X_token.json
    ↓
Bot restarts → Files gone
    ↓
User not connected anymore
    ↓
User: /google → Re-authenticate
```

This is **acceptable** because:
- ✅ Simple to deploy
- ✅ No code changes needed
- ✅ Users re-auth rarely (only after bot restarts)
- ✅ Most users won't notice

### To Make Persistent (Option 2 - Advanced)

We would need to:
1. Create Postgres database on Railway
2. Store credentials in database instead of files
3. Update bot.py to query database
4. Handle credential encryption

**This requires significant code changes. Do this later if needed.**

---

## Procfile Explained

```
worker: python bot.py
```

This tells Railway:
- Run type: **worker** (always running bot, not web server)
- Command: **python bot.py** (what to execute)

That's it! ✨

---

## runtime.txt Explained

```
python-3.11.9
```

This tells Railway:
- Use Python 3.11.9
- (Railway will install this version)

Optional but recommended (ensures compatibility).

---

## Deployment Checklist

- [ ] Have Railway account (free tier works!)
- [ ] Have GitHub repo with bot code
- [ ] Have Telegram bot token
- [ ] Have Google OAuth credentials (client_secrets.json)
- [ ] Set TELEGRAM_BOT_TOKEN in Railway variables
- [ ] Upload/commit client_secrets.json
- [ ] Verify Procfile exists
- [ ] Verify requirements.txt is complete
- [ ] Deploy and test

---

## Common Issues & Fixes

### Issue: "TELEGRAM_BOT_TOKEN not found"
**Fix:** Add to Railway Config Vars
```
TELEGRAM_BOT_TOKEN=your_token
```

### Issue: "client_secrets.json not found"
**Fix:** 
- Option A: Commit to repo
- Option B: Upload manually in Railway
- Option C: Create in Railway shell via deployment logs

### Issue: Bot crashes after few hours
**Fix:** This is the ephemeral filesystem! After 24 hours Railway might recycle the container.
- User needs to `/google` again
- Consider implementing database persistence later

### Issue: "No such file or directory: bot.py"
**Fix:** Procfile should say `python bot.py`
- Check Procfile syntax (exactly as shown above)
- Make sure `bot.py` is in repo root

### Issue: "ModuleNotFoundError"
**Fix:** Missing dependency in requirements.txt
- Should have all these:
  ```
  python-telegram-bot
  python-dotenv
  google-auth-oauthlib
  google-auth-httplib2
  google-api-python-client
  google-auth
  ```

---

## After Deployment

### Monitor the Bot
1. Railway Dashboard → Select project
2. Deployments tab → View logs
3. Look for errors

### Test Functionality
- Send `/start` → Should respond
- Send file → Should save
- Send `/archive` → Should work
- Send `/clear` → Should work

### If Bot Crashes
1. Check Railway logs for errors
2. Check if TELEGRAM_BOT_TOKEN is set
3. Check if client_secrets.json exists
4. Restart deployment from Railway dashboard

---

## Scaling & Advanced

### Free Tier Limits
- ✅ 1 Bot
- ✅ 5GB bandwidth/month
- ✅ Limited storage
- ✅ Decent for testing

### If You Need More
- Consider paid Railway tier
- Add persistent disk
- Add database
- More memory for large files

---

## Credential Persistence (Optional Advanced)

To make credentials persist across restarts, you'd need:

1. **Database** (Postgres or MySQL)
   ```python
   import psycopg2
   conn = psycopg2.connect(DATABASE_URL)
   ```

2. **Store JSON in DB**
   ```python
   cursor.execute(
       "INSERT INTO credentials VALUES (%s, %s)",
       (user_id, json_credentials)
   )
   ```

3. **Retrieve on startup**
   ```python
   creds = cursor.execute(
       "SELECT creds FROM credentials WHERE user_id = %s"
   )
   ```

**We can add this later if needed!** For now, the simple approach works fine.

---

## Summary for Railway Deployment

✅ **Everything needed is ready:**
- Procfile → ✅ Created
- runtime.txt → ✅ Created
- requirements.txt → ✅ Updated
- bot.py → ✅ Complete
- No code changes needed → ✅

⚠️ **One caveat:**
- Credentials won't persist across restarts
- Users will need to re-auth: `/google`
- This is **acceptable** for now

🚀 **You're ready to deploy!**

---

## Quick Deploy Command (if using Railway CLI)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

Or just use the web dashboard - simpler!

---

**Next steps:**
1. Create Railway account
2. Connect GitHub repo
3. Add TELEGRAM_BOT_TOKEN variable
4. Upload client_secrets.json
5. Deploy!

You're all set! 🚀
