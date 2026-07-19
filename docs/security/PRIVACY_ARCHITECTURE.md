# AuthShield Lab — Privacy Architecture

## 1. Overview

AuthShield Lab is a local-first application that processes all data on the user's machine.
This architecture document defines how privacy is embedded into every aspect of the system,
following Privacy by Design principles and aligning with GDPR-like rights.

## 2. Privacy Principles

| # | Principle | Implementation |
|---|-----------|----------------|
| 1 | **Data Minimization** | Collect only what is necessary for educational functionality. |
| 2 | **Purpose Limitation** | Data used only for its stated purpose; no secondary use. |
| 3 | **Local Processing** | All data processing happens on the user's machine. |
| 4 | **User Transparency** | Clear documentation of data handling; data access logs. |
| 5 | **Retention Control** | Configurable retention; automatic cleanup. |
| 6 | **Secure Deletion** | Cryptographic erasure where applicable; secure file deletion. |
| 7 | **User Control** | Users can view, export, and delete all their data. |
| 8 | **No External Transmission** | Zero external network calls; no telemetry; no cloud sync. |

## 3. Data Classification

### 3.1 Classification Matrix

| Data Category | Classification | Examples | Encryption | Retention | User Control |
|---------------|---------------|----------|------------|-----------|--------------|
| Authentication Credentials | Critical | Passwords (hashed), MFA secrets | Argon2id / AES-256 | Account lifetime | Change, delete |
| Session Data | Confidential | Session tokens, device fingerprints | AES-256-GCM | Session lifetime | View, invalidate |
| User Profiles | Internal | Display name, preferences | At-rest encryption | Account lifetime | View, modify, delete |
| Learning Progress | Internal | Module completion, scores | At-rest encryption | Configurable | View, export, delete |
| Assessment Data | Confidential | Answers, grades, timestamps | At-rest encryption | Configurable | View, export, delete |
| Administrative Data | Internal | User roles, permissions | At-rest encryption | Account lifetime | View (admin) |
| Plugin Data | Internal | Plugin state, configuration | Per-plugin encryption | Plugin lifetime | View, delete |
| Audit Logs | Internal | Security events, actions | Integrity chain | Configurable | View (admin) |
| Configuration | Internal | System settings, policies | HMAC-signed | Application lifetime | View, modify |
| Backups | Critical | Encrypted data archives | AES-256-GCM | Configurable | Create, restore, delete |
| Learning Content | Internal | Module content, resources | At-rest encryption | Content lifetime | View |

### 3.2 Data Inventory

| Data Type | Storage Location | Format | Size Estimate |
|-----------|-----------------|--------|---------------|
| User accounts | `database.db` | SQLite | ~1KB per user |
| Session tokens | `database.db` | SQLite | ~200 bytes per session |
| Learning modules | `database.db` | SQLite | ~10KB per module |
| Assessment data | `database.db` | SQLite | ~5KB per assessment |
| Progress data | `database.db` | SQLite | ~1KB per user per module |
| Audit logs | `audit.db` | SQLite | ~500 bytes per entry |
| Configuration | `config.json` | JSON | ~5KB |
| Plugin data | `plugins/` directory | Per-plugin format | Variable |
| Backups | User-designated directory | Encrypted archive | Variable |

## 4. Data Minimization

### 4.1 What We Collect

| Data | Why | Minimum Required |
|------|-----|------------------|
| Username | User identification | Unique identifier |
| Password hash | Authentication | Argon2id hash |
| MFA secret | Multi-factor authentication | TOTP seed |
| Display name | UI personalization | Any non-empty string |
| Learning progress | Track educational progress | Module completion status |
| Assessment answers | Evaluate learning outcomes | Submitted answers |
| Assessment grades | Provide feedback | Calculated scores |
| User role | Access control | Role assignment |
| Audit events | Security and compliance | Event record |

### 4.2 What We Do NOT Collect

| Data | Rationale |
|------|-----------|
| Email addresses | Not required for local-only operation |
| Real names | Username is sufficient |
| IP addresses (external) | Only localhost connections |
| Hardware identifiers | Device fingerprint is local-only |
| Usage analytics | No telemetry by default |
| Learning behavior analytics | No profiling |
| File system contents | No scanning beyond application files |
| Network traffic | No external connections |

### 4.3 Optional Data Collection

Some data is collected only if the user explicitly enables it:

| Data | Default | Opt-In Required |
|------|---------|-----------------|
| Diagnostic data | Disabled | Yes |
| Error reports | Disabled | Yes |
| Performance metrics | Disabled | Yes |
| Security telemetry (exportable) | Enabled locally | No (local only) |

## 5. Purpose Limitation

### 5.1 Purpose Registry

| Data Category | Stated Purpose | Allowed Uses | Prohibited Uses |
|---------------|---------------|--------------|-----------------|
| Authentication | Verify user identity | Login, session management | Tracking, profiling |
| User profiles | Personalization | Display name in UI | Marketing, analytics |
| Learning progress | Educational tracking | Progress display, reporting | Profiling, advertising |
| Assessment data | Learning evaluation | Grading, feedback | Profiling, marketing |
| Audit logs | Security and compliance | Security monitoring, incident response | User profiling |
| Plugin data | Plugin functionality | Plugin operation | Cross-plugin profiling |
| Configuration | System operation | System settings | No secondary use |

### 5.2 Purpose Enforcement

- Code review checks ensure data is used only for stated purposes.
- Automated tests verify no data leakage across purposes.
- Privacy impact assessments review new data uses.
- Annual purpose review ensures continued alignment.

## 6. Local Processing Architecture

### 6.1 Processing Model

```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL PROCESSING MODEL                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    USER'S MACHINE                        │  │
│  │                                                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │ Electron │  │ FastAPI  │  │   SQLite Database     │  │  │
│  │  │  Frontend│──┤ Backend  │──┤   (Encrypted)         │  │  │
│  │  │          │  │          │  │                        │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │  │
│  │                                                           │  │
│  │  All data processing occurs within this boundary         │  │
│  │  No data leaves the machine                              │  │
│  │  No network connections (except localhost)               │  │
│  │  No external API calls                                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  ❌ EXTERNAL SERVICES BLOCKED                            │  │
│  │  • No cloud sync                                         │  │
│  │  • No telemetry endpoints                                │  │
│  │  • No authentication services                            │  │
│  │  • No analytics services                                 │  │
│  │  • No content delivery networks                          │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Network Policy

| Connection Type | Allowed | Rationale |
|----------------|---------|-----------|
| localhost | Yes | Frontend-backend communication |
| LAN (127.0.0.1) | Yes | Localhost binding only |
| External HTTP/HTTPS | No | No external data transmission |
| DNS resolution | No | No external name resolution |
| WebSocket (external) | No | No external connections |
| Multicast/Broadcast | No | No network discovery |

### 6.3 Network Verification

On startup, the application verifies its network posture:

```python
async def verify_network_posture():
    """Verify no unexpected network connections."""
    # Check all listening sockets
    connections = get_all_connections()
    for conn in connections:
        if conn.local_address != "127.0.0.1":
            raise SecurityError(
                f"Unexpected network binding: {conn.local_address}"
            )
    
    # Verify no external connections
    active_connections = get_active_connections()
    for conn in active_connections:
        if not is_localhost(conn.remote_address):
            raise SecurityError(
                f"Unexpected external connection: {conn.remote_address}"
            )
```

## 7. User Transparency

### 7.1 Data Access Logs

Users can view a complete log of how their data has been accessed:

| Access Log Field | Description |
|-----------------|-------------|
| Timestamp | When the access occurred |
| Accessor | Who accessed the data (user, admin, plugin, system) |
| Data Type | What type of data was accessed |
| Purpose | Why the data was accessed |
| Outcome | Whether access was granted or denied |

### 7.2 Transparency Features

| Feature | Description | Access |
|---------|-------------|--------|
| Data Inventory | List of all data types collected | User settings |
| Access History | Log of data access events | User settings |
| Data Usage Report | How data has been used | User settings |
| Privacy Policy | Plain-language privacy documentation | Help menu |
| Data Map | Technical data flow documentation | Documentation |

### 7.3 Data Handling Documentation

The following documentation is maintained and accessible:

| Document | Description | Location |
|----------|-------------|----------|
| Privacy Policy | Plain-language privacy commitments | Help > Privacy Policy |
| Data Map | Technical data flow diagram | Documentation |
| PIA Results | Privacy impact assessment results | Documentation |
| Data Classification | Classification of all data types | This document |
| Retention Schedule | Data retention periods | Documentation |

## 8. Retention Policies

### 8.1 Default Retention Periods

| Data Type | Default Retention | Configurable | Automatic Cleanup |
|-----------|------------------|--------------|-------------------|
| User accounts | Account lifetime | No | On account deletion |
| Session tokens | 8 hours absolute | Yes | Yes |
| Learning progress | 5 years | Yes | Yes |
| Assessment data | 5 years | Yes | Yes |
| Audit logs | 1 year | Yes | Yes |
| Security events | 90 days | Yes | Yes |
| Alert history | 30 days | Yes | Yes |
| Backup archives | Until manual deletion | No | No |
| Plugin data | Plugin lifetime | No | On plugin removal |
| Configuration | Application lifetime | No | On uninstall |
| Diagnostic data | 30 days | Yes | Yes |
| Error reports | 30 days | Yes | Yes |

### 8.2 Retention Enforcement

```python
class RetentionManager:
    """Enforce data retention policies."""
    
    def __init__(self):
        self.policies = load_retention_policies()
    
    async def enforce_retention(self):
        """Run retention enforcement for all data types."""
        for data_type, policy in self.policies.items():
            cutoff_date = datetime.now() - timedelta(days=policy.retention_days)
            
            expired_count = await self.delete_expired(
                data_type=data_type,
                before=cutoff_date
            )
            
            if expired_count > 0:
                await audit_log.record(
                    event="retention.enforcement",
                    data_type=data_type,
                    deleted_count=expired_count,
                    cutoff_date=cutoff_date
                )
    
    async def delete_expired(self, data_type: str, before: datetime):
        """Delete expired data of the specified type."""
        # Implementation varies by data type
        if data_type == "security_events":
            return await self.delete_expired_events(before)
        elif data_type == "audit_logs":
            return await self.delete_expired_logs(before)
        # ... etc
```

### 8.3 Retention Schedule

| Data Type | Schedule | Method |
|-----------|----------|--------|
| Session tokens | On expiry | Automatic |
| Security events | Daily | Automatic |
| Audit logs | Weekly | Automatic |
| Diagnostic data | Weekly | Automatic |
| Error reports | Weekly | Automatic |
| Learning progress | Monthly | Automatic |
| Assessment data | Monthly | Automatic |
| Backup archives | Manual | User-initiated |

## 9. Deletion Policies

### 9.1 Deletion Methods

| Data Type | Deletion Method | Rationale |
|-----------|----------------|-----------|
| Password hashes | Cryptographic erasure (key deletion) | Cannot be recovered |
| Session tokens | Record deletion | Server-side only |
| User profiles | Record deletion | Database operation |
| Learning progress | Record deletion | Database operation |
| Assessment data | Record deletion | Database operation |
| Audit logs | Secure deletion (overwrite + delete) | Tamper resistance |
| Plugin data | Secure file deletion | File system operation |
| Configuration | File deletion | File system operation |
| Backups | Secure file deletion | File system operation |

### 9.2 Account Deletion Process

```
┌─────────────────────────────────────────────────────────────┐
│                  ACCOUNT DELETION PROCESS                     │
│                                                               │
│  1. User requests account deletion                           │
│  2. Identity verification (password + MFA)                   │
│  3. Confirmation dialog (typed confirmation)                 │
│  4. Invalidate all active sessions                           │
│  5. Soft-delete user account                                 │
│  6. Anonymize audit log entries (remove PII)                 │
│  7. Delete user data:                                        │
│     - Profile data                                           │
│     - Learning progress                                      │
│     - Assessment data                                        │
│     - Plugin data                                            │
│     - Session data                                           │
│  8. Cryptographic erasure of authentication credentials      │
│  9. Record deletion event in audit log                       │
│ 10. Hard-delete account record                               │
│ 11. Verify deletion completeness                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 Deletion Verification

After deletion, the system verifies:

- No records exist for the deleted user.
- No PII remains in audit logs (anonymized).
- No plugin data remains for the deleted user.
- No session data remains.
- Backup archives do not contain recoverable user data (future backups).

## 10. Export Controls

### 10.1 User Data Export

Users can export all their data at any time:

| Export Format | Contents | Access |
|---------------|----------|--------|
| JSON | Complete user data | User auth required |
| CSV | Tabular data (progress, assessments) | User auth required |
| PDF | Progress report | User auth required |

### 10.2 Export Process

```
┌─────────────────────────────────────────────────────────────┐
│                    USER DATA EXPORT                           │
│                                                               │
│  1. User requests data export                                │
│  2. Identity verification (password)                         │
│  3. Assemble user data from all sources:                     │
│     - Profile data                                           │
│     - Learning progress                                      │
│     - Assessment data and grades                             │
│     - Session history                                        │
│     - Plugin data (per-plugin)                               │
│  4. Format data in requested format                          │
│  5. Generate export archive                                  │
│  6. Log export event in audit trail                          │
│  7. Provide download to user                                 │
│  8. Securely delete temporary export files                   │
└─────────────────────────────────────────────────────────────┘
```

### 10.3 Export Data Structure

```json
{
  "export_version": "1.0",
  "export_date": "ISO-8601",
  "user_id": "anonymized_id",
  "data": {
    "profile": {
      "username": "user",
      "display_name": "User Name",
      "created_at": "ISO-8601",
      "preferences": {}
    },
    "learning_progress": [
      {
        "module_id": "module_1",
        "status": "completed",
        "score": 85,
        "completed_at": "ISO-8601"
      }
    ],
    "assessments": [
      {
        "assessment_id": "assess_1",
        "module_id": "module_1",
        "submitted_at": "ISO-8601",
        "score": 90,
        "answers": {}
      }
    ],
    "sessions": [
      {
        "session_id": "anonymized",
        "created_at": "ISO-8601",
        "last_active": "ISO-8601"
      }
    ],
    "plugin_data": {
      "plugin_1": {}
    }
  }
}
```

## 11. Backup Privacy

### 11.1 Backup Encryption

| Property | Value |
|----------|-------|
| Algorithm | AES-256-GCM |
| Key Derivation | Argon2id (memory-hard) |
| Key Source | User-provided passphrase |
| Nonce | Random 96-bit per backup |
| Authentication | GCM authentication tag |

### 11.2 Backup Access Control

| Action | Requirement |
|--------|-------------|
| Create backup | Admin authentication |
| View backup metadata | Admin authentication |
| Restore backup | Admin authentication + passphrase |
| Delete backup | Admin authentication + confirmation |
| Export backup | Admin authentication + audit logging |

### 11.3 Backup Contents

Backups include:

| Included | Rationale |
|----------|-----------|
| Database (encrypted) | User data preservation |
| Configuration (encrypted) | System settings preservation |
| Audit trail (encrypted) | Compliance requirement |
| Plugin data (encrypted) | Plugin state preservation |

Backups do NOT include:

| Excluded | Rationale |
|----------|-----------|
| Encryption keys | Derived from passphrase at restore |
| Temporary files | Not user data |
| Cache files | Regenerated automatically |
| Log files (non-audit) | Operational, not user data |

## 12. GDPR-Like Rights

### 12.1 Rights Implementation

| Right | Implementation | User Action |
|-------|----------------|-------------|
| **Right of Access** | Data export feature | Export All Data |
| **Right to Rectification** | Profile modification | Edit Profile |
| **Right to Erasure** | Account deletion | Delete Account |
| **Right to Data Portability** | Data export in standard format | Export All Data |
| **Right to Restrict Processing** | Disable features | Privacy Settings |
| **Right to Object** | Feature opt-out | Privacy Settings |
| **Right to be Informed** | Privacy policy, data map | Help > Privacy |

### 12.2 Rights Workflow

| Right | Workflow | Timeline |
|-------|----------|----------|
| Access | Request → Verify → Assemble → Export → Deliver | Immediate |
| Rectification | Request → Verify → Modify → Confirm | Immediate |
| Erasure | Request → Verify → Confirm → Delete → Verify | Within 24 hours |
| Portability | Request → Verify → Export → Deliver | Immediate |
| Restriction | Request → Verify → Restrict → Confirm | Immediate |
| Objection | Request → Verify → Disable → Confirm | Immediate |

## 13. Privacy Impact Assessment Template

### 13.1 PIA Sections

| Section | Questions |
|---------|-----------|
| **Feature Description** | What does the feature do? What problem does it solve? |
| **Data Flows** | What data does the feature access? Where does data flow? |
| **Data Collection** | What new data is collected? Is it necessary? |
| **Data Processing** | How is data processed? Is processing local? |
| **Data Storage** | Where is data stored? Is it encrypted? |
| **Data Retention** | How long is data retained? Can retention be shortened? |
| **Data Sharing** | Is data shared with any third parties? |
| **User Rights** | How are user rights affected? |
| **Risks** | What privacy risks does the feature introduce? |
| **Mitigations** | How are privacy risks mitigated? |
| **Necessity** | Is the data collection proportionate to the purpose? |
| **Consent** | Is user consent required? How is consent obtained? |

### 13.2 PIA Decision Matrix

| Risk Level | Likelihood | Impact | Action |
|------------|-----------|--------|--------|
| Low | Low | Low | Document and proceed |
| Medium | Any | Medium or Low | Implement mitigations and proceed |
| High | Any | High or Medium | Implement mitigations; require security sign-off |
| Critical | Any | Any | Redesign feature to reduce risk |

## 14. Privacy Documentation

### 14.1 Required Documentation

| Document | Audience | Update Frequency |
|----------|----------|------------------|
| Privacy Policy | Users | Annually |
| Data Map | Developers, Auditors | Per feature change |
| PIA Results | Security Team | Per feature |
| Retention Schedule | Administrators | Quarterly |
| Deletion Procedures | Administrators | Per change |
| Export Procedures | Users, Administrators | Per change |

### 14.2 Privacy Policy Structure

| Section | Content |
|---------|---------|
| Introduction | What AuthShield Lab is; local-first commitment |
| Data We Collect | Complete list of data types collected |
| How We Use Data | Purpose limitation statement |
| Local Processing | All processing on user's machine |
| No External Transmission | No data leaves the machine |
| Data Retention | Retention periods per data type |
| Your Rights | Access, rectification, erasure, portability |
| Data Security | How data is protected |
| Changes to Policy | How policy changes are communicated |
| Contact | How to reach the team |

## 15. Privacy Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Data minimization compliance | 100% | No unnecessary data collected |
| External network connections | 0 | Network monitoring |
| Retention policy compliance | 100% | Automated enforcement |
| User data export success rate | 100% | Export operation logging |
| Account deletion completeness | 100% | Post-deletion verification |
| PIA completion for new features | 100% | PIA tracking |
| Privacy documentation currency | 100% | Documentation review |
