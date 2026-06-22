# Database Documentation

This directory contains documentation for database schemas, operations, and management.

## Contents

### Database Reference
- Database schemas and design
- Table definitions
- Indexes and optimization
- Query patterns

### Operations & Maintenance
- Backup procedures
- Recovery procedures
- Performance tuning
- Monitoring and alerts

### Administration
- User management
- Permission management
- Maintenance tasks
- Troubleshooting

## Database Overview

The _codex_ system uses multiple databases:

- **Primary Database**: PostgreSQL (default)
- **Cache Store**: Redis
- **Search Index**: Elasticsearch (optional)
- **Time Series**: InfluxDB (optional)

## Quick Reference

### Connection Information

```yaml
host: localhost
port: 5432
database: codex
user: codex_user
```

### Key Tables

- `users`: User account information
- `models`: ML model registry
- `experiments`: Training experiments
- `runs`: Individual training runs
- `metrics`: Performance metrics
- `artifacts`: Generated artifacts

## Common Tasks

### Database Backup

```bash
# Create backup
pg_dump codex > backup_$(date +%Y%m%d).sql

# Restore from backup
psql codex < backup_20260620.sql
```

## Performance Tuning

1. Analyze query performance
2. Create necessary indexes
3. Update statistics
4. Archive old data
5. Monitor resource usage

### User Management

- Create database users
- Assign permissions
- Reset passwords
- Audit access logs

## Troubleshooting

### Common Issues

**Connection refused**
- Check database service status
- Verify connection parameters
- Check firewall rules
- Review error logs

**Performance degradation**
- Analyze query plans
- Check index usage
- Monitor resource utilization
- Consider data archiving

**Data integrity issues**
- Run consistency checks
- Review transaction logs
- Perform recovery procedures
- Update statistics

## Monitoring

Key metrics to monitor:
- Connection count
- Query response time
- Disk space usage
- Replication lag
- Cache hit ratio

## Maintenance Procedures

### Daily
- Monitor alerts
- Check backup completion
- Review slow queries

### Weekly
- Analyze index usage
- Update statistics
- Review capacity trends

### Monthly
- Full backup verification
- Disaster recovery testing
- Performance analysis
- Archive old data

## Related Documentation

- [Admin Documentation](../admin/)
- [Operations Guide](../operations/)
- [Security Documentation](../security/)
- [Troubleshooting Guide](../troubleshooting/)

## Maintenance

Last updated: 2026-06-20
Status: Active
Owner: @mbaetiong

For database issues, contact the database administration team.
