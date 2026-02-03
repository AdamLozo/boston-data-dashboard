# Render Deployment Instructions

## Step 1: Deploy from render.yaml (Blueprint)

1. Go to Render Dashboard: https://dashboard.render.com/

2. Click **"New +"** button (top right) → Select **"Blueprint"**

3. Connect your GitHub repository:
   - Click **"Connect a repository"**
   - Find and select: `AdamLozo/boston-data-dashboard`
   - Click **"Connect"**

4. Render will automatically detect `render.yaml` and show you:
   - **Database**: boston-dashboard-db (PostgreSQL)
   - **Web Service**: boston-data-dashboard
   - **Cron Job**: boston-dashboard-sync

5. Click **"Apply"** to start deployment

6. Wait for all 3 services to deploy (5-10 minutes):
   - Database will be created first
   - Web service will build and deploy
   - Cron job will be configured

## Step 2: Run Initial Data Sync

After deployment completes:

1. Go to **Cron Jobs** → Click on `boston-dashboard-sync`

2. Click **"Trigger Run"** to manually run the first sync
   - This will populate the database with 90 days of permits
   - Takes about 30-60 seconds
   - Check logs to verify success

3. Verify data loaded:
   - Go to your web service URL
   - You should see the dashboard with permit data
   - Check `/api/health` endpoint

## Step 3: Configure Custom Domain

### Add Custom Domain to Render

1. Go to **Web Services** → Click on `boston-data-dashboard`

2. Go to **Settings** tab → Scroll to **Custom Domains**

3. Click **"Add Custom Domain"**

4. Enter: `bostonbuildingpermits.adamlozo.com`

5. Render will provide DNS instructions showing:
   - **CNAME Record**: Point to your Render service URL

### Configure DNS (at your domain registrar)

1. Go to your DNS provider for `adamlozo.com`

2. Add a CNAME record:
   - **Name/Host**: `bostonbuildingpermits`
   - **Type**: CNAME
   - **Value/Target**: `boston-data-dashboard.onrender.com` (or the URL Render provides)
   - **TTL**: 3600 (or automatic)

3. Save the DNS record

4. Wait for DNS propagation (5-60 minutes)

5. Return to Render and click **"Verify DNS"**

6. Once verified, Render will automatically provision SSL certificate

### Expected URLs

- **Render Default**: `https://boston-data-dashboard.onrender.com`
- **Custom Domain**: `https://bostonbuildingpermits.adamlozo.com`

## Step 4: Verify Everything Works

Check these endpoints:

1. **Dashboard**: https://bostonbuildingpermits.adamlozo.com
   - Should show interactive map with permits
   - Filters should work

2. **Health Check**: https://bostonbuildingpermits.adamlozo.com/api/health
   - Should return `{"status": "healthy"}`

3. **API Docs**: https://bostonbuildingpermits.adamlozo.com/docs
   - FastAPI auto-generated documentation

## Step 5: Monitor

1. **Cron Job Schedule**: Runs daily at 6 AM EST (11:00 UTC)

2. **Check Logs**:
   - Web Service logs for API requests
   - Cron Job logs for sync status

3. **Database**:
   - Monitor via Render dashboard
   - Check usage under Database → Metrics

## Troubleshooting

### If build fails:
- Check logs for Python dependency errors
- Verify `requirements.txt` has all dependencies

### If cron job fails:
- Check environment variables are set
- Verify DATABASE_URL is connected
- Check logs for CKAN API errors

### If custom domain doesn't work:
- Wait 60 minutes for DNS propagation
- Verify CNAME record is correct
- Check DNS with: `nslookup bostonbuildingpermits.adamlozo.com`

## Costs

- **Database**: ~$7/month (Starter plan)
- **Web Service**: Free tier (or $7/month for Starter)
- **Cron Job**: Free tier
- **Total**: ~$7-14/month depending on tier

## Auto-Deploy

Any push to `main` branch will automatically redeploy the web service.

To disable: Web Service → Settings → Auto-Deploy (toggle off)
