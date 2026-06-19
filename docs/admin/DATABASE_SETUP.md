# Database Setup & Configuration Guide

> **Version**: 2.0.0  
> **Last Updated**: 2026-06-20  
> **Audience**: DevOps, system administrators, operators

---

## Quick Start (10 minutes)

### Option 1: SQLite (Development/Testing)

```bash
# SQLite is built-in to Python
python -c "import sqlite3; print('✅ SQLite ready')"

# Connection string for config
DATABASE_URL="sqlite:///./codex.db"
```

### Option 2: PostgreSQL (Production)

```bash
# Install PostgreSQL
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql

# Start service
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Create database
createdb codex_production

# Connection string
DATABASE_URL="******localhost:5432/codex_production"
```

### Option 3: Docker (Any Database)

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: codex
      POSTGRES_USER: codex_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Start:**
```bash
docker-compose up -d
# Connection: ******localhost:5432/codex
```

---

## Database Migration

### Initialize Schema

```bash
# Using Alembic (recommended)
alembic upgrade head

# Or using direct SQL
psql -U codex_user -d codex_production < schema.sql
```

### Run Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## Backup & Recovery

### Regular Backups

```bash
# PostgreSQL backup
pg_dump -U codex_user codex_production > backup_2026-06-20.sql

# Restore from backup
psql -U codex_user codex_production < backup_2026-06-20.sql

# Automated daily backups
0 2 * * * pg_dump -U user codex > /backups/codex_$(date +\%Y-\%m-\%d).sql
```

### Backup Verification

```bash
# Check backup integrity
psql -U codex_user -d test_restore < backup.sql > /dev/null 2>&1 && echo "✅ Backup OK" || echo "❌ Backup corrupt"
```

---

## Performance Optimization

### Indexing

```sql
-- Create indexes for common queries
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_embedding_doc_id ON embeddings(doc_id);
CREATE INDEX idx_timestamp ON events(created_at);
```

### Query Optimization

```sql
-- ❌ SLOW: N+1 query problem
SELECT * FROM users;
-- Then for each user: SELECT * FROM orders WHERE user_id = ?

-- ✅ FAST: Join
SELECT u.*, o.* FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check service running, verify credentials |
| Disk space full | Increase volume, archive old data |
| High memory usage | Add indexes, optimize queries, increase buffer |
| Slow queries | Check indexes, analyze execution plans |

---

**Last Updated:** 2026-06-20
