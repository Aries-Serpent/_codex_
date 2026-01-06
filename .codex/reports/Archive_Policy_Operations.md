# Archive Policy Operations

## Archive Operations Log
- Maintain a detailed log of all archiving operations performed, including timestamps, user actions, and affected records.

## SQL Storage
- Archiving should involve moving data to a dedicated SQL storage system.
- Ensure that the archived data is still queryable and retrievable when needed.

### Example SQL Archive Structure:
```sql
CREATE TABLE archived_data (
    id SERIAL PRIMARY KEY,
    data JSONB,
    archived_at TIMESTAMP DEFAULT NOW()
);
```text

## Tombstone Creation
- Create tombstones for records that are archived to indicate their status.
- Tombstones should include metadata about the archived record.

### Example Tombstone Structure:
- Record ID: 1234
- Archived At: 2023-10-15 12:00:00
- Reason for Archiving: Data no longer needed

## Evidence Logging with Core Files
- Ensure that all core files related to archiving operations are logged as evidence.
- Documentation paths should be clearly defined for all archived records.

### Example Evidence Logging:
- Core File: `data_backup_2023_10_15.zip`
- Documentation Path: `./documentation/backup_logs/2023/10/15/`

## Actual Examples
1. **Archiving User Data**: 
   - Log the user data archiving process with a timestamp and user ID.
   - Move data to the SQL storage and create a tombstone.

2. **Archiving Logs**:  
   - Regularly archive logs older than 90 sessions and create evidence logs for audit purposes.