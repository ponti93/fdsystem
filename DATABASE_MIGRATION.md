# 🗄️ Database Migration Guide - Local to Render PostgreSQL

## 🎯 Migration Strategy

**Current**: Local PostgreSQL → **Target**: Render Managed PostgreSQL

## 📋 Migration Steps

### Step 1: Export Local Data
```bash
# Export your current database
cd backend
pg_dump -h localhost -U postgres -d new_fdsystem_db > local_backup.sql

# Export only data (no schema)
pg_dump -h localhost -U postgres -d new_fdsystem_db --data-only > local_data.sql
```

### Step 2: Create Render Database
1. **Render Dashboard** → Add PostgreSQL database
2. **Database Name**: `fraud_detection_db`
3. **Plan**: Free tier
4. **Region**: Same as web service

### Step 3: Get Render Database Credentials
```
DATABASE_HOST=<render-postgres-host>
DATABASE_PORT=5432
DATABASE_NAME=fraud_detection_db
DATABASE_USER=postgres
DATABASE_PASSWORD=<render-generated-password>
DATABASE_URL=postgresql://postgres:<password>@<host>:5432/fraud_detection_db
```

### Step 4: Update Environment Variables
Update your `.env` file and Render service environment variables:
```env
# Replace local database settings
DATABASE_HOST=<render-postgres-host>
DATABASE_PORT=5432
DATABASE_NAME=fraud_detection_db
DATABASE_USER=postgres
DATABASE_PASSWORD=<render-postgres-password>
```

### Step 5: Schema Migration
The schema will be automatically created on first deployment via `init_database()` in startup event.

### Step 6: Data Migration (Optional)
If you want to keep your local transactions and users:

```bash
# Connect to Render database and import data
psql "postgresql://postgres:<password>@<host>:5432/fraud_detection_db" < local_data.sql
```

## 🔄 Migration Verification

### Test Checklist:
- [ ] ✅ Database connection successful
- [ ] ✅ All tables created (users, transactions, fraud_assessments, fraud_rules)
- [ ] ✅ Sample data populated
- [ ] ✅ ML model can save/load
- [ ] ✅ Transactions process correctly
- [ ] ✅ Analytics display data

### Health Check:
```bash
curl https://your-app.onrender.com/health
# Should return: {"status": "healthy", "database": "connected"}
```

## 🚨 Rollback Plan

### If Migration Fails:
1. **Keep local database** running
2. **Revert environment variables** to local settings
3. **Test local system** still works
4. **Debug Render issues** separately

### Backup Strategy:
- **Before migration**: Export full local database
- **After migration**: Verify Render database works
- **Keep backups**: Store local dumps safely

## 🎯 Production Considerations

### Environment Variables Security:
- **Never commit** real API keys to GitHub
- **Use Render environment variables** for secrets
- **Keep .env.example** with dummy values

### Database Performance:
- **Free tier limitations**: 1GB storage, limited connections
- **Monitor usage**: Check Render dashboard
- **Upgrade if needed**: Consider paid database plan for production

## 📊 Expected Timeline

- **Setup Render Database**: 5 minutes
- **Update Environment Variables**: 10 minutes  
- **Deploy and Test**: 15 minutes
- **Data Migration** (if needed): 30 minutes
- **Total**: ~1 hour for complete migration

## 🔗 Useful Links

- [Render PostgreSQL Documentation](https://render.com/docs/databases)
- [Environment Variables Guide](https://render.com/docs/environment-variables)
- [PostgreSQL Connection Strings](https://render.com/docs/databases#connecting-to-your-database)
