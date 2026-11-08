import { create } from 'zustand';
import type { Theme, UserRole, Notification, AccessibilityPreferences, BreadcrumbItem } from '../types';

export interface AppState {
  theme: Theme;
  sidebarCollapsed: boolean;
  sidebarActivePage: string;
  currentMode: UserRole;
  notifications: Notification[];
  unreadNotificationCount: number;
  searchQuery: string;
  searchOpen: boolean;
  breadcrumbs: BreadcrumbItem[];
  user: {
    id: string;
    username: string;
    displayName: string;
    email: string;
    avatar?: string;
    role: UserRole;
  } | null;
  accessibility: AccessibilityPreferences;
}

export interface AppActions {
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSidebarActivePage: (page: string) => void;
  setCurrentMode: (mode: UserRole) => void;
  addNotification: (notification: Notification) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  clearNotifications: () => void;
  removeNotification: (id: string) => void;
  setSearchQuery: (query: string) => void;
  setSearchOpen: (open: boolean) => void;
  setBreadcrumbs: (breadcrumbs: BreadcrumbItem[]) => void;
  updateUser: (updates: Partial<AppState['user']>) => void;
  updateAccessibility: (updates: Partial<AccessibilityPreferences>) => void;
  reset: () => void;
}

const defaultAccessibility: AccessibilityPreferences = {
  highContrast: false,
  reducedMotion: false,
  fontSize: 'medium',
  keyboardNav: true,
  screenReader: false,
  dyslexiaFont: false,
  spacing: 'normal',
};

const initialState: AppState = {
  theme: 'dark',
  sidebarCollapsed: false,
  sidebarActivePage: '/dashboard',
  currentMode: 'demo',
  notifications: [],
  unreadNotificationCount: 0,
  searchQuery: '',
  searchOpen: false,
  breadcrumbs: [{ label: 'Dashboard', path: '/dashboard' }],
  user: {
    id: 'user-1',
    username: 'admin',
    displayName: 'Admin User',
    email: 'admin@authshieldlab.dev',
    role: 'administrator',
  },
  accessibility: defaultAccessibility,
};

export const useAppStore = create<AppState & AppActions>((set, get) => ({
  ...initialState,

  setTheme: (theme) => {
    set({ theme });
    if (typeof window !== 'undefined') {
      localStorage.setItem('authshield-theme', theme);
    }
  },

  toggleTheme: () => {
    const { theme } = get();
    const next: Theme = theme === 'dark' ? 'light' : theme === 'light' ? 'dark' : theme;
    get().setTheme(next);
  },

  toggleSidebar: () => {
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },

  setSidebarCollapsed: (collapsed) => {
    set({ sidebarCollapsed: collapsed });
  },

  setSidebarActivePage: (page) => {
    set({ sidebarActivePage: page });
  },

  setCurrentMode: (mode) => {
    set({ currentMode: mode });
  },

  addNotification: (notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadNotificationCount: state.unreadNotificationCount + (notification.read ? 0 : 1),
    }));
  },

  markNotificationRead: (id) => {
    set((state) => {
      const notification = state.notifications.find((n) => n.id === id);
      if (!notification || notification.read) return state;
      return {
        notifications: state.notifications.map((n) =>
          n.id === id ? { ...n, read: true } : n
        ),
        unreadNotificationCount: Math.max(0, state.unreadNotificationCount - 1),
      };
    });
  },

  markAllNotificationsRead: () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadNotificationCount: 0,
    }));
  },

  clearNotifications: () => {
    set({ notifications: [], unreadNotificationCount: 0 });
  },

  removeNotification: (id) => {
    set((state) => {
      const notification = state.notifications.find((n) => n.id === id);
      return {
        notifications: state.notifications.filter((n) => n.id !== id),
        unreadNotificationCount:
          state.unreadNotificationCount - (notification && !notification.read ? 1 : 0),
      };
    });
  },

  setSearchQuery: (query) => {
    set({ searchQuery: query });
  },

  setSearchOpen: (open) => {
    set({ searchOpen: open });
  },

  setBreadcrumbs: (breadcrumbs) => {
    set({ breadcrumbs });
  },

  updateUser: (updates) => {
    set((state) => ({
      user: state.user ? { ...state.user, ...updates } : null,
    }));
  },

  updateAccessibility: (updates) => {
    set((state) => ({
      accessibility: { ...state.accessibility, ...updates },
    }));
  },

  reset: () => {
    set(initialState);
  },
}));
