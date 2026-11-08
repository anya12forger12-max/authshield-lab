# Administrator Guide

This guide covers system administration tasks for AuthShield Lab.

## Initial Setup

### First Run

1. Start the application in Admin mode
2. Create the initial administrator account
3. Configure system settings
4. Set up user accounts or import from CSV
5. Configure security policies

### Creating Admin Account

```bash
# Using CLI
python -m app.users.create --email admin@example.com --role admin --name "Admin User"
```

Or through the web interface:

1. Launch the application
2. Click "Create Admin Account"
3. Enter credentials and display name
4. Confirm account creation

## User Management

### Creating Users

1. Navigate to **Users** module
2. Click **Create User**
3. Fill in required fields:
   - Email address
   - Display name
   - Role (Student, Instructor, Admin, Developer)
4. Set initial password
5. Click **Create**

### Bulk Import

Prepare a CSV file with columns:

```csv
email,name,role
user1@example.com,User One,student
user2@example.com,User Two,student
instructor@example.com,Instructor One,instructor
```

Import via:
1. Navigate to **Users** module
2. Click **Import**
3. Select CSV file
4. Review and confirm

### User Roles

| Role | Permissions |
|------|------------|
| **Student** | View modules, complete lessons, run guided simulations |
| **Instructor** | All student permissions + create sessions, grade, reports |
| **Admin** | Full access including user management and system settings |
| **Developer** | Full access + API explorer, debug tools, logs |

### Deactivating Users

Deactivating preserves data while preventing access:

1. Select user in User Management
2. Click **Deactivate**
3. Confirm action

Deactivated users can be reactivated at any time.

### Password Management

**Reset Password**:
1. Select user
2. Click **Reset Password**
3. Generate temporary password or set custom

**Force Password Change**:
1. Select user
2. Enable **Force Change on Next Login**

**Password Policy**:
- Minimum length: 8 characters (configurable)
- Require uppercase, lowercase, numbers, special characters
- Password history: Prevent reuse of last 12 passwords
- Expiration: Configurable (default: 90 days)

## Security Configuration

### Session Management

Configure in **Settings > Security**:

| Setting | Default | Description |
|---------|---------|-------------|
| Session Timeout | 30 min | Inactivity timeout |
| Max Sessions | 3 | Concurrent sessions per user |
| Token Expiry | 15 min | JWT access token lifetime |
| Refresh Expiry | 7 days | Refresh token lifetime |
| Single Session | Off | Enforce one session per user |

### Rate Limiting

Configure per-endpoint rate limits:

| Endpoint | Default Limit | Window |
|----------|--------------|--------|
| `/api/auth/login` | 5 requests | 1 minute |
| `/api/auth/register` | 3 requests | 5 minutes |
| `/api/auth/password/reset` | 3 requests | 15 minutes |
| `/api/*` | 100 requests | 1 minute |

### Account Lockout

| Setting | Default | Description |
|---------|---------|-------------|
| Lockout Threshold | 5 | Failed attempts before lockout |
| Lockout Duration | 15 min | Time before auto-unlock |
| Reset Counter | 30 min | Time to reset failure count |

### IP Blocking

Configure automatic IP blocking:

- Enable/disable IP blocking
- Set block duration
- Maintain blocklist
- Whitelist trusted addresses

## Database Management

### Backup

```bash
# Manual backup
cp data/app.db backups/app-$(date +%Y%m%d).db

# Automated backup (set up cron/scheduled task)
0 2 * * * cp /path/to/data/app.db /path/to/backups/app-$(date +\%Y\%m\%d).db
```

### Restore

```bash
# Stop the application first
cp backups/app-20240115.db data/app.db
# Restart the application
```

### Maintenance

**Vacuum Database** (reclaim space):

```sql
VACUUM;
```

**Check Integrity**:

```sql
PRAGMA integrity_check;
```

**View Statistics**:

```sql
SELECT name, COUNT(*) as count FROM sqlite_master WHERE type='table' GROUP BY name;
```

### Migration

```bash
cd backend
alembic upgrade head    # Apply migrations
alembic downgrade -1    # Rollback last migration
alembic history        # View migration history
```

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/api/health
```

Response:

```json
{
  "status": "healthy",
  "database": "connected",
  "uptime": 86400,
  "version": "1.0.0-alpha.1"
}
```

### Log Files

| Log | Location | Description |
|-----|----------|-------------|
| Application | `logs/app.log` | General application events |
| Access | `logs/access.log` | HTTP request logs |
| Error | `logs/error.log` | Error and exception logs |
| Audit | `logs/audit.log` | Security audit events |

### Log Rotation

Configure log rotation to prevent disk space issues:

```bash
# /etc/logrotate.d/authshield
/path/to/authshield/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
}
```

## Network Configuration

### Localhost Binding

AuthShield Lab binds to `127.0.0.1` by default. This is a security requirement.

**Do not** configure:
- External IP binding
- 0.0.0.0 binding
- Port forwarding to the application
- Reverse proxy to external networks

### Firewall Rules

The application does not require external network access. Ensure:

- No inbound rules for the application ports
- No outbound rules from the application
- Localhost traffic is not blocked

### CORS Configuration

CORS is restricted to local origins:

```env
APP_CORS_ORIGINS=["http://localhost:5173","http://localhost:8000"]
```

Do not add external origins.

## Compliance

### Audit Requirements

AuthShield Lab maintains:

- Immutable audit logs for all actions
- User access records
- Configuration change history
- Security event documentation

### Data Retention

| Data Type | Default Retention | Configurable |
|-----------|------------------|--------------|
| Audit Logs | 90 days | Yes |
| Access Logs | 30 days | Yes |
| Session Data | 30 days | Yes |
| User Data | Until deleted | N/A |
| Attack Results | 365 days | Yes |

### Compliance Standards

The platform supports compliance checking for:
- SOX (Sarbanes-Oxley)
- HIPAA
- PCI-DSS
- GDPR
- NIST CSF

Run compliance checks from the **Compliance Checker** module.

## Backup Strategy

### Daily Backups

```bash
#!/bin/bash
# daily-backup.sh
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"
cp data/app.db "$BACKUP_DIR/app-$DATE.db"

# Keep only last 30 days
find "$BACKUP_DIR" -name "app-*.db" -mtime +30 -delete
```

### Scheduled Task (Windows)

```cmd
schtasks /create /tn "AuthShield Backup" /tr "C:\path\to\daily-backup.bat" /sc daily /st 02:00
```

### Cron Job (Linux/macOS)

```bash
0 2 * * * /path/to/daily-backup.sh
```

## Troubleshooting

### Application Won't Start

1. Check port availability: `lsof -i :8000` or `netstat -ano | findstr :8000`
2. Verify database exists: `ls data/app.db`
3. Check logs: `tail -f logs/app.log`
4. Verify Python environment: `which python`

### Database Locked

```bash
# Check for other processes using the database
lsof data/app.db  # Linux/macOS
# Close other instances of the application
```

### High Memory Usage

1. Check session count (too many active sessions)
2. Review audit log size
3. Restart the application periodically
4. Monitor with `htop` or Task Manager

### Performance Issues

1. Vacuum the database periodically
2. Archive old audit logs
3. Check disk space
4. Monitor CPU and memory usage

## Updating

```bash
# 1. Backup database
cp data/app.db backups/pre-update.db

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Run migrations
cd ../backend && alembic upgrade head

# 5. Rebuild frontend
cd ../frontend && npm run build

# 6. Restart application
```

## Support

- Documentation: [docs/](../docs/)
- Issues: [GitHub Issues](https://github.com/authshieldlab/authshield-lab/issues)
- Security: See [SECURITY.md](../../SECURITY.md)
