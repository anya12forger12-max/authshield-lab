# ADR-003: SQLite over PostgreSQL

## Status

Accepted

## Context

AuthShield Lab requires a database for storing users, sessions, attack configurations, audit logs, and learning progress. Since this is a desktop application running locally, we evaluated:

1. **SQLite**: Embedded, zero-configuration database
2. **PostgreSQL**: Full-featured client-server relational database

## Decision

We chose **SQLite** as the primary database.

## Rationale

### Advantages of SQLite

- **Zero Configuration**: No server to install, configure, or maintain
- **Embedded**: Database is a single file that moves with the application
- **Portability**: Users can backup by copying a single file
- **Performance**: For single-user/local workloads, SQLite is extremely fast
- **Reliability**: ACID compliant with WAL mode for concurrent reads
- **Size**: No separate database process; minimal overhead
- **Deployment**: No database server required in production
- **Security**: Database file can be encrypted with SQLCipher if needed

### Why PostgreSQL Wasn't Chosen

- **Installation Complexity**: PostgreSQL requires separate installation, configuration, and service management
- **Resource Usage**: PostgreSQL's background processes consume memory and CPU unnecessarily for a local application
- **Deployment Overhead**: Users would need to install and configure PostgreSQL before using the application
- **Overkill**: PostgreSQL's advanced features (replication, partitioning, full-text search) are unnecessary for local data
- **Portability**: Database backup/restore requires pg_dump/pg_restore rather than simple file copy

### When Would We Reconsider

- If we need concurrent multi-user access from multiple machines
- If data volume exceeds SQLite's practical limits (~140TB theoretical, ~281TB practical)
- If we need advanced PostgreSQL features like JSONB, arrays, or full-text search
- If we add server-side deployment option

## Consequences

### Positive

- Simple deployment with no database server requirement
- Easy backup (copy single file)
- Fast development and testing
- Low resource consumption
- Portable application data

### Negative

- Limited concurrent write performance
- No built-in network access (by design, which is actually a security benefit)
- Limited to single-machine usage
- No advanced PostgreSQL features

### Mitigations

- Use WAL mode for better concurrent read performance
- Implement proper connection pooling for SQLite
- Use SQLAlchemy for future database migration capability if needed
- Archive old data to prevent database bloat

## Technical Details

### SQLite Configuration

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA foreign_keys=ON;
PRAGMA temp_store=MEMORY;
PRAGMA mmap_size=268435456;
```

### SQLAlchemy Configuration

```python
DATABASE_URL = "sqlite+aiosqlite:///./data/app.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```
