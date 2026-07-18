export type Theme = 'light' | 'dark' | 'system' | 'high-contrast-dark' | 'high-contrast-light';

export type UserRole = 'demo' | 'student' | 'instructor' | 'administrator' | 'developer';

export type AppMode = UserRole;

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavItem[];
  badge?: number | string;
  requiredRole?: UserRole[];
  group?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: string;
}

export interface AccessibilityPreferences {
  highContrast: boolean;
  reducedMotion: boolean;
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
  keyboardNav: boolean;
  screenReader: boolean;
  dyslexiaFont: boolean;
  spacing: 'compact' | 'normal' | 'relaxed';
}

export interface User {
  id: string;
  username: string;
  email: string;
  displayName: string;
  avatar?: string;
  role: UserRole;
  createdAt: string;
  lastLoginAt: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: Theme;
  accessibility: AccessibilityPreferences;
  notifications: NotificationPreferences;
  language: string;
  timezone: string;
}

export interface NotificationPreferences {
  email: boolean;
  browser: boolean;
  inApp: boolean;
  securityAlerts: boolean;
  sessionAlerts: boolean;
}

export interface Session {
  id: string;
  userId: string;
  username: string;
  ipAddress: string;
  userAgent: string;
  location?: string;
  startedAt: string;
  lastActiveAt: string;
  expiresAt: string;
  isActive: boolean;
  device?: string;
  browser?: string;
}

export interface SecurityEvent {
  id: string;
  type: SecurityEventType;
  severity: EventSeverity;
  title: string;
  description: string;
  source: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
  userId?: string;
  sessionId?: string;
}

export type SecurityEventType =
  | 'authentication_success'
  | 'authentication_failure'
  | 'brute_force_detected'
  | 'credential_stuffing'
  | 'session_hijack_attempt'
  | 'privilege_escalation'
  | 'tokenForgery'
  | 'mfa_bypass_attempt'
  | 'password_spray'
  | 'account_lockout'
  | 'suspicious_login'
  | 'defense_activated'
  | 'defense_bypassed'
  | 'rule_triggered';

export type EventSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical';

export interface AttackScenario {
  id: string;
  name: string;
  description: string;
  category: AttackCategory;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  techniques: string[];
  estimatedDuration: string;
  learningObjectives: string[];
  prerequisites: string[];
}

export type AttackCategory =
  | 'credential_attack'
  | 'session_attack'
  | 'token_attack'
  | 'mfa_bypass'
  | 'privilege_escalation'
  | 'social_engineering';

export interface DefenseRule {
  id: string;
  name: string;
  description: string;
  category: DefenseCategory;
  enabled: boolean;
  effectiveness: number;
  falsePositiveRate: number;
}

export type DefenseCategory =
  | 'rate_limiting'
  | 'account_lockout'
  | 'captcha'
  | 'ip_reputation'
  | 'anomaly_detection'
  | 'mfa_enforcement'
  | 'session_protection'
  | 'token_validation';

export interface AnalyticsData {
  totalEvents: number;
  authenticationAttempts: number;
  successfulAuth: number;
  failedAuth: number;
  blockedAttacks: number;
  activeSessions: number;
  securityScore: number;
  threatsOverTime: TimeSeriesData[];
  attackDistribution: CategoryData[];
  defenseEffectiveness: DefenseMetric[];
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  label?: string;
}

export interface CategoryData {
  category: string;
  count: number;
  percentage: number;
}

export interface DefenseMetric {
  ruleId: string;
  ruleName: string;
  triggeredCount: number;
  blockedCount: number;
  effectiveness: number;
}

export interface BreadcrumbItem {
  label: string;
  path: string;
  isCurrent?: boolean;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
}

export interface LearningModule {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  lessons: Lesson[];
  completedLessons: number;
  totalLessons: number;
}

export interface Lesson {
  id: string;
  title: string;
  type: 'text' | 'video' | 'interactive' | 'quiz';
  duration: string;
  completed: boolean;
}

export interface AuditLogEntry {
  id: string;
  userId: string;
  username: string;
  action: string;
  resource: string;
  resourceId?: string;
  details?: Record<string, unknown>;
  ipAddress: string;
  timestamp: string;
  outcome: 'success' | 'failure';
}

export interface TimelineEvent {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  severity: EventSeverity;
  relatedEvents: string[];
}

export interface ReportConfig {
  id: string;
  name: string;
  type: 'security' | 'compliance' | 'activity' | 'performance';
  dateRange: { start: string; end: string };
  format: 'pdf' | 'csv' | 'json';
  sections: string[];
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'radar' | 'area';
  title: string;
  data: unknown;
  options?: Record<string, unknown>;
}

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  column: string;
  direction: SortDirection;
}

export interface FilterConfig {
  field: string;
  operator: 'equals' | 'contains' | 'startsWith' | 'endsWith' | 'gt' | 'lt' | 'between';
  value: string | number | boolean;
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}
