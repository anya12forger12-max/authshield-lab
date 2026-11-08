import type { NavItem } from '../types';

export const navigationConfig: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'LayoutDashboard',
    path: '/dashboard',
    group: 'Main',
  },
  {
    id: 'authentication',
    label: 'Authentication',
    icon: 'Lock',
    path: '/authentication',
    group: 'Security',
    children: [
      { id: 'auth-methods', label: 'Auth Methods', icon: 'Key', path: '/authentication/methods' },
      { id: 'auth-config', label: 'Configuration', icon: 'Settings', path: '/authentication/configuration' },
    ],
  },
  {
    id: 'users',
    label: 'Users',
    icon: 'Users',
    path: '/users',
    group: 'Security',
    requiredRole: ['administrator', 'instructor'],
  },
  {
    id: 'sessions',
    label: 'Sessions',
    icon: 'Monitor',
    path: '/sessions',
    group: 'Security',
  },
  {
    id: 'attacks',
    label: 'Attacks',
    icon: 'Swords',
    path: '/attacks',
    group: 'Simulation',
  },
  {
    id: 'defenses',
    label: 'Defenses',
    icon: 'Shield',
    path: '/defenses',
    group: 'Simulation',
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: 'BarChart3',
    path: '/analytics',
    group: 'Monitoring',
  },
  {
    id: 'audit',
    label: 'Audit Logs',
    icon: 'FileText',
    path: '/audit',
    group: 'Monitoring',
    requiredRole: ['administrator', 'instructor'],
  },
  {
    id: 'timeline',
    label: 'Security Timeline',
    icon: 'Clock',
    path: '/timeline',
    group: 'Monitoring',
  },
  {
    id: 'reports',
    label: 'Reports',
    icon: 'FileBarChart',
    path: '/reports',
    group: 'Education',
    requiredRole: ['administrator', 'instructor', 'developer'],
  },
  {
    id: 'learning',
    label: 'Learning Center',
    icon: 'GraduationCap',
    path: '/learning',
    group: 'Education',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: 'Settings',
    path: '/settings',
    group: 'System',
    requiredRole: ['administrator'],
  },
  {
    id: 'help',
    label: 'Help',
    icon: 'HelpCircle',
    path: '/help',
    group: 'System',
  },
];

export const navigationGroups = [
  { id: 'Main', label: 'Main' },
  { id: 'Security', label: 'Security' },
  { id: 'Simulation', label: 'Simulation' },
  { id: 'Monitoring', label: 'Monitoring' },
  { id: 'Education', label: 'Education' },
  { id: 'System', label: 'System' },
];

export function getNavItemsByGroup(items: NavItem[]): Record<string, NavItem[]> {
  const groups: Record<string, NavItem[]> = {};
  for (const item of items) {
    const group = item.group || 'Other';
    if (!groups[group]) groups[group] = [];
    groups[group].push(item);
  }
  return groups;
}

export function getNavItemsByRole(items: NavItem[], role: string): NavItem[] {
  return items.filter((item) => {
    if (!item.requiredRole) return true;
    return item.requiredRole.includes(role as never);
  });
}
