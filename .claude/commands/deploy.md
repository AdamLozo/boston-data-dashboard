# Deploy Command

Push code to GitHub and verify Render deployment.

## Prerequisites
- Git configured
- GitHub repo created (boston-data-dashboard)
- Render services configured

## Steps

1. Stage and commit changes:
```bash
git add -A
git commit -m "Description of changes"
```

2. Push to main (triggers auto-deploy):
```bash
git push origin main
```

3. Monitor deployment:
- Open Render Dashboard
- Check service logs for build/deploy status
- Wait for "Live" status

4. Verify deployment:
```bash
curl "https://boston-data-dashboard.onrender.com/api/health"
```

## First Deployment Checklist

- [ ] GitHub repo created
- [ ] render.yaml in repo root
- [ ] Push to GitHub
- [ ] Connect repo to Render
- [ ] Database auto-provisions
- [ ] Web service deploys
- [ ] Cron job configured

## Troubleshooting

**Build failed**: Check Render logs, verify requirements.txt
**Database connection error**: Check DATABASE_URL env var in Render
**Cron not running**: Verify schedule in render.yaml
