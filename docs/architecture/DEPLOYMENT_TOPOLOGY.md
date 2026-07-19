# Deployment Topology — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Overview

AuthShield Lab supports **8 deployment topologies** tailored to different environments and use cases. All topologies share the same codebase but differ in configuration, packaging, and storage layout.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT TOPOLOGIES                            │
│                                                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐  │
│  │ Portable  │  │ Installed │  │Institution│  │  Standalone   │  │
│  │ Edition   │  │ Edition   │  │    al     │  │   Desktop     │  │
│  └───────────┘  └───────────┘  └───────────┘  └───────────────┘  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐  │
│  │ Offline   │  │ Training  │  │University │  │  Government   │  │
│  │Lab Environ│  │  Center   │  │Deployment │  │  Deployment   │  │
│  └───────────┘  └───────────┘  └───────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Portable Edition (USB/Flash Drive)

### 2.1 Overview

Run AuthShield Lab entirely from a USB drive. No installation required. Data persists on the drive.

### 2.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Electron binary | `portable/electron/` | Pre-built, platform-specific |
| Backend (Python) | `portable/python/` | Embedded Python runtime |
| Application code | `portable/app/` | Bundled with installer |
| SQLite database | `portable/data/app.db` | Created on first run |
| Configuration | `portable/config/` | Default settings |

### 2.2 Optional Components

| Component | Purpose | Size |
|---|---|---|
| Plugin samples | Demo plugins | ~5MB |
| Content library | Pre-loaded courses | ~50MB |
| Offline docs | Full documentation | ~20MB |
| Backup copies | Previous data backups | Variable |

### 2.3 Storage Layout

```
USB_DRIVE/
├── portable/
│   ├── electron/           # Electron binaries (~150MB)
│   │   ├── authshield.exe  # (or .app on macOS)
│   │   └── resources/
│   ├── python/             # Embedded Python (~100MB)
│   │   ├── python.exe
│   │   └── lib/
│   ├── app/                # Application code (~20MB)
│   │   ├── backend/
│   │   └── renderer/
│   ├── config/             # Configuration (~1KB)
│   │   ├── settings.json
│   │   └── user_preferences.json
│   ├── data/               # Data directory (created at runtime)
│   │   ├── app.db          # SQLite database
│   │   ├── backups/        # Backup files
│   │   ├── logs/           # Log files
│   │   ├── plugins/        # Installed plugins
│   │   └── exports/        # Exported reports
│   └── launch.bat          # Windows launch script
│   └── launch.sh           # Linux/macOS launch script
└── README.txt              # Setup instructions
```

### 2.4 Configuration Strategy

| Setting | Value | Rationale |
|---|---|---|
| Database location | `portable/data/app.db` | Relative to portable root |
| Log level | INFO | Minimal storage usage |
| Backup frequency | Manual only | USB write cycle preservation |
| Auto-update | Disabled | No network on USB machines |
| Plugin sandbox | Strict | Maximum security on shared machines |

### 2.5 Upgrade Strategy

1. Download new portable package
2. Copy `config/`, `data/`, `plugins/` from old to new
3. Run migration if database schema changed
4. Verify data integrity
5. Old USB retained as fallback

### 2.6 Backup Strategy

| Strategy | Frequency | Retention |
|---|---|---|
| Manual backup | User-triggered | Keep last 3 |
| Pre-upgrade backup | Before upgrade | Keep until verified |
| No auto-backup | — | USB write cycle preservation |

---

## 3. Installed Edition (Per-Machine)

### 3.1 Overview

Standard desktop installation with full OS integration. Data stored in user's application data directory.

### 3.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Electron app | `/opt/authshield/` or `AppData/` | OS-standard location |
| Backend (Python) | Bundled in app | Frozen binary |
| SQLite database | `~/.authshield/data/app.db` | User data directory |
| Configuration | `~/.authshield/config/` | User config directory |

### 3.3 Optional Components

| Component | Purpose |
|---|---|
| Auto-updater | Check for new versions (offline manifest) |
| System tray | Background running |
| Start menu entry | Easy launch |
| File associations | `.asplugin`, `.asbackup` files |
| Context menu | Right-click integration |

### 3.4 Storage Layout

```
~/.authshield/
├── data/
│   ├── app.db              # Main database
│   ├── backups/            # Automated backups
│   ├── logs/               # Application logs
│   ├── plugins/            # Installed plugins
│   └── exports/            # Exported data
├── config/
│   ├── settings.json       # Application settings
│   └── user_preferences.json
└── cache/
    └── analytics_cache.db  # Analytics cache
```

### 3.5 Configuration Strategy

| Setting | Value | Rationale |
|---|---|---|
| Database location | `~/.authshield/data/` | XDG-compliant |
| Log level | INFO | Standard usage |
| Backup frequency | Daily at 02:00 | Automated |
| Auto-update | Check daily (offline manifest) | Keep current |
| Plugin sandbox | Standard | Normal security |

### 3.6 Upgrade Strategy

1. New version installer launched
2. Current database backed up automatically
3. Application binary replaced
4. Migrations run on first launch
5. User notified of upgrade success
6. Previous version retained for 7 days

### 3.7 Backup Strategy

| Strategy | Frequency | Retention |
|---|---|---|
| Automated daily | 02:00 | Last 30 days |
| Pre-upgrade | Before upgrade | Until next upgrade |
| On-demand | User-triggered | Until manual delete |

---

## 4. Institutional Deployment (Multi-Seat)

### 4.1 Overview

Deployed across an organization with centralized configuration and shared content. Each seat has its own database.

### 4.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Central configuration | Network share (read-only) | Shared settings |
| Per-seat installation | Each workstation | Installed Edition |
| Content repository | Network share (read-only) | Shared courses |
| License server | Local network (optional) | License management |

### 4.3 Optional Components

| Component | Purpose |
|---|---|
| Admin console | Centralized management |
| Content distribution | Course deployment |
| License management | Seat tracking |
| Centralized logging | Aggregate logs (optional) |
| Shared plugins | Organization plugins |

### 4.4 Storage Layout

```
NETWORK_SHARE/authshield/
├── config/
│   ├── organization_settings.json    # Org-wide settings
│   └── content_manifest.json         # Available content
├── content/
│   ├── courses/                      # Shared courses
│   ├── plugins/                      # Shared plugins
│   └── templates/                    # Shared templates
├── docs/                             # Organization documentation
└── licenses/
    └── license.json                  # License file

LOCAL_MACHINE (~/.authshield/)
├── data/                             # Per-seat data
├── config/
│   ├── settings.json                 # Local overrides
│   └── user_preferences.json         # Per-user prefs
└── cache/
```

### 4.5 Configuration Strategy

| Setting | Source | Override |
|---|---|---|
| Organization settings | Network share | Read-only |
| Local settings | Local config | Overrides org |
| User preferences | Local config | Overrides all |
| Content path | Network share | Read-only |
| Plugin path | Network share + local | Merged |

### 4.6 Upgrade Strategy

1. IT department updates network share with new version
2. Admin triggers deployment script
3. Each seat pulls update from network share
4. Local databases migrated individually
5. Rollback plan: revert network share to previous version

### 4.7 Backup Strategy

| Strategy | Frequency | Location |
|---|---|---|
| Per-seat backup | Daily | Local backups/ |
| Content backup | Weekly | Network share backup |
| Configuration backup | After changes | Network share backup |

---

## 5. Standalone Desktop

### 5.1 Overview

Single-user installation on a personal computer. Full feature set with maximum customization.

### 5.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Electron app | OS-standard location | Full installation |
| SQLite database | `~/.authshield/data/` | User data |
| Full plugin support | `~/.authshield/plugins/` | All plugins |
| Full content library | Bundled + user-imported | All content |

### 5.3 Optional Components

| Component | Purpose |
|---|---|
| Auto-update | Version management |
| System tray | Always running |
| Desktop shortcut | Quick access |
| File associations | `.asplugin` files |
| Shell integration | Context menu, drag-drop |

### 5.4 Configuration Strategy

| Setting | Value | Rationale |
|---|---|---|
| All features | Enabled | Full functionality |
| Backup | Daily automated | Data protection |
| Auto-update | Check daily | Stay current |
| Plugin sandbox | Standard | Normal security |
| Log level | WARNING | Minimal output |

### 5.5 Upgrade Strategy

1. Auto-update notifies of new version
2. User approves upgrade
3. Current state backed up
4. Binary replaced, migrations run
5. Application restarts with new version

### 5.6 Backup Strategy

| Strategy | Frequency | Retention |
|---|---|---|
| Automated daily | 02:00 | 30 days |
| Pre-upgrade | Before upgrade | 30 days |
| On-demand | User-triggered | Until delete |

---

## 6. Offline Lab Environment (Computer Lab)

### 6.1 Overview

Deployed in a computer lab with no internet access. Multiple users share workstations across different sessions.

### 6.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Lab image | System image | Pre-installed on all machines |
| Shared content | Network share (local) | Lab-specific courses |
| Per-user data | User profile or lab account | Isolated per user |
| Lab management | Admin console | Configuration management |

### 6.3 Optional Components

| Component | Purpose |
|---|---|
| User profile sync | roaming profiles |
| Lab reset script | Restore to clean state |
| Assessment repository | Lab-specific assessments |
| Instructor dashboard | Monitor student progress |

### 6.4 Storage Layout

```
LAB_IMAGE/
├── authshield/                    # Pre-installed application
│   ├── electron/
│   ├── python/
│   └── app/
├── lab_content/                   # Shared content (read-only)
│   ├── courses/
│   ├── assessments/
│   └── simulations/
└── lab_config/                    # Lab configuration
    ├── settings.json              # Lab-wide settings
    └── user_template.json         # Default user preferences

USER_PROFILE/
├── .authshield/
│   ├── data/
│   │   ├── app.db                # Per-user database
│   │   ├── backups/
│   │   └── exports/
│   └── config/
│       └── user_preferences.json
```

### 6.5 Configuration Strategy

| Setting | Value | Rationale |
|---|---|---|
| Content path | Lab network share | Shared courses |
| Backup | Disabled | Lab reset restores state |
| Auto-update | Disabled | Lab image management |
| Plugin install | Disabled | Lab admin only |
| Log level | WARNING | Minimal output |
| Session timeout | 30 min idle | Lab fairness |

### 6.6 Upgrade Strategy

1. Lab admin creates new lab image
2. Image deployed via lab management system
3. User data preserved via profile sync
4. Old image retained for rollback

### 6.7 Backup Strategy

| Strategy | Frequency | Retention |
|---|---|---|
| Lab image backup | Before changes | Until next update |
| User data | Not backed up | Lab reset restores |
| Lab content | Weekly | Version controlled |

---

## 7. Training Center Deployment

### 7.1 Overview

Deployed in a professional training center with instructor-led sessions, student tracking, and certification management.

### 7.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Application | All workstations | Full installation |
| Instructor dashboard | Instructor machine | Central monitoring |
| Student tracking | Database | Progress tracking |
| Assessment engine | All machines | Exam delivery |
| Content delivery | Network share | Course materials |
| Certification system | Central server | Certificate generation |

### 7.3 Optional Components

| Component | Purpose |
|---|---|
| Live progress feed | Real-time student progress |
| Lab assignment system | Course-to-workstation mapping |
| Print server | Certificate printing |
| Video recording | Session recording |
| Whiteboard integration | Collaborative features |

### 7.4 Storage Layout

```
TRAINING_CENTER/
├── server/
│   ├── instructor_db.db          # Central database
│   ├── student_databases/        # Per-student databases
│   ├── content/                  # Course content
│   ├── assessments/              # Assessment bank
│   ├── certifications/           # Certificate templates
│   └── reports/                  # Generated reports
├── instructor_machine/
│   └── dashboard/                # Instructor dashboard app
└── student_workstations/
    └── .authshield/              # Per-student local data
```

### 7.5 Configuration Strategy

| Setting | Value | Rationale |
|---|---|---|
| Content path | Central server | Shared courses |
| Backup | After each session | Student progress protection |
| Auto-update | Disabled | Controlled updates |
| Plugin install | Restricted | Instructor-approved only |
| Session tracking | Enabled | Progress monitoring |
| Certification | Enabled | Certificate generation |

### 7.6 Upgrade Strategy

1. Training center admin schedules upgrade window
2. All machines updated during off-hours
3. Student data migrated centrally
4. Verification testing on sample machines
5. Rollback plan if issues detected

### 7.7 Backup Strategy

| Strategy | Frequency | Retention |
|---|---|---|
| Student data | After each session | Training period |
| Instructor data | Daily | 90 days |
| Content | Weekly | Version controlled |
| Certificates | After each issue | Permanent |

---

## 8. University Deployment

### 8.1 Overview

Deployed in a university setting for cybersecurity courses. Integrates with LMS (Moodle, Canvas) via file import/export. Multi-semester support.

### 8.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Application | Lab machines + student laptops | Mixed deployment |
| Course content | University LMS export | Moodle/Canvas compatible |
| Gradebook integration | CSV import/export | LMS grade sync |
| Multi-semester support | Database partitioning | Per-semester data |
| Research data export | Anonymized export | Research compliance |

### 8.3 Optional Components

| Component | Purpose |
|---|---|
| LTI integration | LMS tool integration |
| Research analytics | Anonymized usage data |
| Plagiarism detection | Assessment integrity |
| Peer review module | Collaborative assessment |
| Thesis project tools | Capstone project support |

### 8.4 Storage Layout

```
UNIVERSITY_DEPLOYMENT/
├── department/
│   ├── courses/
│   │   ├── CS301_Security/        # Per-course content
│   │   ├── CS401_AdvancedSec/
│   │   └── CS501_Capstone/
│   ├── assessments/
│   │   ├── question_bank/         # Shared question bank
│   │   └── rubrics/               # Assessment rubrics
│   └── research/
│       └── anonymized_data/       # Research datasets
├── student_machines/
│   └── .authshield/
│       ├── data/
│       │   └── app.db            # Per-student data
│       └── config/
└── instructor_machines/
    └── .authshield/
        ├── data/
        │   └── app.db            # Instructor database
        └── config/
```

### 8.5 Configuration Strategy

| Setting | Value | Rationale |
|---|---|---|
| Content path | Department network | Shared courses |
| Backup | Before semester end | Grade protection |
| Auto-update | Semester break only | Stability |
| Research export | Enabled | Research compliance |
| Plagiarism check | Per assignment | Academic integrity |
| Multi-semester | Enabled | Course continuity |

### 8.6 Upgrade Strategy

1. Upgrade scheduled during semester break
2. All machines updated before semester start
3. Previous semester data archived
4. New semester content loaded
5. Student data migrated or reset per policy

### 8.7 Backup Strategy

| Strategy | Frequency | Retention |
|---|---|---|
| Grade data | After each class | Permanent |
| Student progress | Weekly | Semester + 1 |
| Content | Per version | Permanent |
| Research data | Per study | Per IRB requirements |

---

## 9. Government Deployment

### 9.1 Overview

Deployed in government agencies with strict security, compliance, and audit requirements. Air-gapped networks. FIPS-compliant crypto.

### 9.2 Required Components

| Component | Location | Notes |
|---|---|---|
| Application | Classified network | Air-gapped |
| FIPS crypto module | Bundled | FIPS 140-2 compliant |
| Audit system | Centralized audit server | Tamper-proof logs |
| Compliance engine | Real-time | NIST/ISO compliance |
| Security scanning | Continuous | Vulnerability assessment |
| Access control | Strict RBAC | Need-to-know basis |

### 9.3 Optional Components

| Component | Purpose |
|---|---|
| STIG compliance | DISA STIG checks |
| X.509 certificate auth | PKI integration |
| Hardware security module | Key storage |
| Network monitoring | Traffic analysis |
| Incident response | Automated response |

### 9.4 Storage Layout

```
GOVERNMENT_DEPLOYMENT/
├── secure_zone/
│   ├── application/
│   │   ├── authshield/            # Application binaries
│   │   ├── fips_crypto/           # FIPS crypto module
│   │   └── compliance/            # Compliance rules
│   ├── data/
│   │   ├── classified_db.db       # Classified data
│   │   ├── audit_logs/            # Tamper-proof audit
│   │   └── compliance_reports/    # Compliance evidence
│   └── keys/
│       ├── encryption_keys/       # Encrypted key store
│       └── signing_keys/          # Code signing keys
├── admin_console/
│   └── security_dashboard/        # Security monitoring
└── backup_vault/
    └── encrypted_backups/         # Secure backup storage
```

### 9.5 Configuration Strategy

| Setting | Value | Rationale |
|---|---|---|
| Encryption | FIPS 140-2 | Government requirement |
| Audit level | Maximum | Complete audit trail |
| Backup | Continuous | Zero data loss |
| Auto-update | Disabled | Manual security review |
| Plugin install | Prohibited | Security lockdown |
| Log retention | 7 years | Government compliance |
| Session timeout | 15 min idle | Security policy |

### 9.6 Upgrade Strategy

1. Security team reviews new version
2. FIPS compliance verified
3. Vulnerability assessment completed
4. Deployment authorized by security officer
5. Phased rollout (test group → full deployment)
6. Rollback plan documented and tested

### 9.7 Backup Strategy

| Strategy | Frequency | Retention |
|---|---|---|
| Real-time replication | Continuous | Zero data loss |
| Daily full backup | 02:00 | 7 years |
| Archive backup | Monthly | Permanent |
| Offsite backup | Weekly | 7 years |

---

## 10. Topology Comparison Matrix

| Feature | Portable | Installed | Institutional | Standalone | Lab | Training | University | Government |
|---|---|---|---|---|---|---|---|---|
| Installation | None | Standard | Multi-seat | Standard | Image | Central | Mixed | Secure |
| Data location | USB | User dir | User dir | User dir | User dir | Central | User dir | Secure zone |
| Network required | No | No | Partial | No | Partial | Partial | Partial | No |
| Multi-user | No | No | Yes | No | Yes | Yes | Yes | Yes |
| Plugin support | Full | Full | Controlled | Full | Restricted | Restricted | Full | Disabled |
| Backup strategy | Manual | Auto | Auto | Auto | Reset | Auto | Auto | Continuous |
| Update strategy | Manual | Auto | IT managed | Auto | Image | Admin | Semester | Security review |
| Compliance | Basic | Basic | Org policy | Basic | Lab policy | Training policy | Academic | Government |
| Security level | Standard | Standard | Org standard | Standard | Lab standard | Training standard | Academic | Maximum |
| Audit level | Minimal | Standard | Org standard | Standard | Minimal | Standard | Standard | Maximum |

---

## 11. Cross-Topology Features

### 11.1 Universal Features

All topologies share:
- Same codebase and module set
- Same SQLite database format
- Same plugin architecture
- Same accessibility features
- Same security baseline
- Same offline-first design

### 11.2 Topology Detection

```python
class TopologyDetector:
    def detect(self) -> Topology:
        if self._is_portable():
            return Topology.PORTABLE
        if self._is_lab():
            return Topology.LAB
        if self._is_institutional():
            return Topology.INSTITUTIONAL
        if self._is_government():
            return Topology.GOVERNMENT
        if self._is_university():
            return Topology.UNIVERSITY
        if self._is_training_center():
            return Topology.TRAINING_CENTER
        return Topology.STANDALONE
```

### 11.3 Configuration Profiles

Each topology has a default configuration profile:

```json
{
  "topology": "portable",
  "database": {"path": "portable/data/app.db"},
  "backup": {"enabled": false},
  "auto_update": {"enabled": false},
  "plugins": {"sandbox": "strict", "install_allowed": true},
  "logging": {"level": "INFO", "retention_days": 7},
  "security": {"level": "standard", "fips_mode": false}
}
```
