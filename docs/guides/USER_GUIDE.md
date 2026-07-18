# User Guide

This guide explains how to use AuthShield Lab in its various modes.

## Getting Started

After launching AuthShield Lab, you will see the login screen. Your application mode determines what features are available to you.

### Application Modes

#### Demo Mode

**For**: Evaluators and potential users

Demo mode provides a read-only showcase of the platform with pre-populated sample data. No login required.

**Available features**:
- Browse all modules
- View sample dashboards and reports
- See attack simulation results
- Explore learning center content

**Limitations**:
- Cannot create or modify data
- Cannot run live simulations
- All data is read-only

#### Student Mode

**For**: Learners enrolled in training courses

Student mode provides guided access to training modules with progress tracking.

**Available features**:
- Complete learning modules and quizzes
- Run guided attack simulations
- View personal progress and analytics
- Earn badges and certificates
- Access learning center resources

**Workflow**:
1. Log in with your student credentials
2. Browse the Learning Center for courses
3. Complete modules in sequence
4. Take quizzes to test knowledge
5. Track progress on your Dashboard

#### Instructor Mode

**For**: Teachers and trainers

Instructor mode adds classroom management and assessment capabilities.

**Additional features**:
- Create and manage training sessions
- Monitor student progress
- Grade assessments
- Generate student reports
- Customize attack scenarios

#### Admin Mode

**For**: System administrators

Admin mode provides full platform configuration access.

**Additional features**:
- User management (create, edit, deactivate)
- System settings configuration
- Security policy management
- Database maintenance
- Audit log access
- Backup and restore

#### Developer Mode

**For**: Platform contributors and testers

Developer mode includes debugging tools and API exploration.

**Additional features**:
- API explorer with request builder
- Database query interface
- Log viewer with filtering
- Performance profiler
- WebSocket inspector
- Feature flags control

## Navigation

### Sidebar

The left sidebar provides access to all modules:

- **Dashboard**: Platform overview and metrics
- **Authentication**: Login and auth settings
- **Users**: User directory and management
- **Sessions**: Active and historical sessions
- **Attacks**: Attack simulation library
- **Defenses**: Defense mechanism configuration
- **Analytics**: Metrics and visualizations
- **Reports**: Report generation and history
- **Learning**: Courses and training content
- **Audit**: Activity audit trail
- **Timeline**: Event timeline view
- **Settings**: Platform configuration
- **Help**: Documentation and support

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open quick search |
| `Ctrl+/` | Toggle sidebar |
| `Ctrl+1-9` | Navigate to module |
| `Ctrl+Shift+P` | Command palette |
| `Esc` | Close modal/dialog |
| `?` | Show keyboard shortcuts |

### Quick Search

Press `Ctrl+K` to open the quick search bar. Type to search across:

- Modules and pages
- Users and sessions
- Attack types
- Documentation topics

## Module Guides

### Dashboard

The Dashboard provides an at-a-glance view of platform status.

**Widgets**:
- **Metrics Cards**: Key counts (users, sessions, attacks, defenses)
- **Activity Feed**: Recent platform events
- **Charts**: Attack/defense trend lines
- **Quick Actions**: Common operations

**Customization**:
- Drag widgets to rearrange
- Click widget headers to collapse
- Use the settings icon to show/hide widgets

### Authentication Module

Manage authentication settings and view auth-related data.

**Sections**:
- **Login History**: All authentication attempts
- **Password Policy**: Current complexity requirements
- **MFA Status**: Multi-factor authentication enrollment
- **Token Management**: Active JWT tokens

### User Management

Create and manage user accounts.

**Operations**:
- **Create User**: Add new user with role assignment
- **Edit User**: Modify profile and permissions
- **Deactivate User**: Disable account without deletion
- **Bulk Import**: CSV import for multiple users
- **User Details**: View user activity and sessions

### Attack Simulations

Run security attack simulations for learning purposes.

**Attack Types**:
1. Select an attack type from the library
2. Configure attack parameters
3. Select target (user or endpoint)
4. Execute the simulation
5. Review results and analysis

**Parameters**:
- Attack intensity (low/medium/high)
- Duration limit
- Target selection
- Logging verbosity

**Safety Features**:
- All attacks are simulated against local data only
- No real credentials are tested
- Results are for educational purposes only

### Defense Mechanisms

Configure and monitor defensive measures.

**Available Defenses**:
- Rate Limiting: Set request limits per user/IP
- Account Lockout: Configure lockout thresholds
- CAPTCHA: Enable challenge-response verification
- IP Blocking: Block suspicious addresses
- MFA Enforcement: Require multi-factor auth

**Monitoring**:
- View real-time defense triggers
- See blocked attempts
- Analyze defense effectiveness

### Analytics

Explore platform metrics and trends.

**Views**:
- **Overview**: Key metrics summary
- **Attacks**: Attack frequency and types
- **Defenses**: Defense trigger rates
- **Users**: User activity patterns
- **Sessions**: Session duration and count
- **Custom**: Build custom metric views

**Export**: Download data as CSV or JSON

### Reports

Generate security and training reports.

**Report Types**:
- Security Summary
- Attack Analysis
- Defense Effectiveness
- User Activity
- Compliance Status

**Steps**:
1. Select report type
2. Configure date range and filters
3. Preview report
4. Generate and download

### Learning Center

Access educational content and track progress.

**Features**:
- **Course Catalog**: Browse available courses
- **Lessons**: Read through learning materials
- **Quizzes**: Test your knowledge
- **Labs**: Hands-on exercises
- **Progress**: Track completion
- **Certificates**: Earn completion badges

### Audit Trail

Review platform activity logs.

**Features**:
- **Event List**: Chronological activity log
- **Advanced Search**: Filter by user, action, time
- **Event Details**: Full event information
- **Export**: Download filtered logs

### Timeline

Visualize event sequences chronologically.

**Features**:
- **Timeline View**: Events on a time axis
- **Event Clustering**: Group related events
- **Zoom**: Focus on specific time ranges
- **Annotations**: Add investigation notes

### Settings

Configure platform behavior and appearance.

**Categories**:
- **General**: Application name, mode, language
- **Security**: Password policy, session timeout
- **Appearance**: Theme, font size, accessibility
- **Notifications**: Alert preferences
- **Backup**: Database backup schedule

### Help

Access documentation and support resources.

**Resources**:
- **Documentation**: Searchable help articles
- **Keyboard Shortcuts**: Reference guide
- **Interactive Tutorial**: Platform walkthrough
- **About**: Version and build information

## Personalization

### Themes

Choose from five built-in themes:
- **Light**: Standard light theme
- **Dark**: Easy on the eyes dark theme
- **High Contrast**: Maximum contrast for visibility
- **Dyslexia Friendly**: OpenDyslexic font with adjusted spacing
- **Solarized**: Warm color palette

### Accessibility

- **Font Size**: Adjustable from 12px to 24px
- **Reduced Motion**: Disable animations
- **Keyboard Navigation**: Full keyboard access
- **Screen Reader**: ARIA labels throughout
- **Focus Indicators**: Visible focus rings

## Data Management

### Exporting Data

Most modules support data export:
- CSV for spreadsheet analysis
- JSON for programmatic use
- PDF for reports

### Local Storage

All data is stored locally on your machine:
- Database: `data/app.db`
- Logs: `logs/`
- Config: `~/.config/authshield-lab/`

No data is sent to external servers.

## Troubleshooting

### Application Won't Start

1. Check that port 8000 is not in use
2. Verify the backend is running
3. Check `logs/` for error messages

### Login Issues

1. Ensure correct username and password
2. Check if account is locked (too many failed attempts)
3. Contact administrator for password reset

### Slow Performance

1. Close other applications to free resources
2. Check database size (large databases may be slow)
3. Reduce the number of active sessions displayed
4. Clear the audit log if it's very large

### Missing Features

Features available depend on your application mode. Contact your administrator to request access to additional features.
