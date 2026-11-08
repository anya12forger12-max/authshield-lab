# AuthShield Lab — Localization UI Framework

> Internationalization and localization specification for the offline-first desktop cybersecurity education platform.

---

## 1. Overview

AuthShield Lab supports a global audience of cybersecurity professionals and students. The UI framework must handle multiple languages, scripts, text expansion, right-to-left layouts, and locale-specific formatting. This document defines the complete localization UI framework.

---

## 2. Supported Locales

| Locale | Language | Script | Direction |
|--------|----------|--------|-----------|
| `en-US` | English (US) | Latin | LTR (default) |
| `en-GB` | English (UK) | Latin | LTR |
| `de-DE` | German | Latin | LTR |
| `fr-FR` | French | Latin | LTR |
| `es-ES` | Spanish | Latin | LTR |
| `pt-BR` | Portuguese (Brazil) | Latin | LTR |
| `ja-JP` | Japanese | CJK | LTR |
| `ko-KR` | Korean | Hangul | LTR |
| `zh-CN` | Chinese (Simplified) | Han | LTR |
| `zh-TW` | Chinese (Traditional) | Han | LTR |
| `ar-SA` | Arabic | Arabic | RTL |
| `he-IL` | Hebrew | Hebrew | RTL |
| `ru-RU` | Russian | Cyrillic | LTR |
| `tr-TR` | Turkish | Latin | LTR |

---

## 3. Right-to-Left (RTL) Support

### 3.1 Layout Mirroring

When an RTL locale is active, the entire layout mirrors horizontally:

```
LTR Layout:
┌──────┬────────────────────┬──────────┐
│ Nav  │     Workspace      │ Inspector│
│ Rail │                    │  Panel   │
│ (48) │                    │  (300)   │
└──────┴────────────────────┴──────────┘

RTL Layout:
┌──────────┬────────────────────┬──────┐
│Inspector │     Workspace      │ Nav  │
│  Panel   │                    │ Rail │
│  (300)   │                    │ (48) │
└──────────┴────────────────────┴──────┘
```

### 3.2 CSS Logical Properties

Use CSS logical properties instead of physical properties:

| Physical Property | Logical Property | Behavior |
|-------------------|-----------------|----------|
| `margin-left` | `margin-inline-start` | Left in LTR, Right in RTL |
| `margin-right` | `margin-inline-end` | Right in LTR, Left in RTL |
| `padding-left` | `padding-inline-start` | Left in LTR, Right in RTL |
| `padding-right` | `padding-inline-end` | Right in LTR, Left in RTL |
| `text-align: left` | `text-align: start` | Left in LTR, Right in RTL |
| `text-align: right` | `text-align: end` | Right in LTR, Left in RTL |
| `border-left` | `border-inline-start` | Left in LTR, Right in RTL |
| `border-right` | `border-inline-end` | Right in LTR, Left in RTL |
| `left` | `inset-inline-start` | Left in LTR, Right in RTL |
| `right` | `inset-inline-end` | Right in LTR, Left in RTL |
| `float: left` | `float: inline-start` | Left in LTR, Right in RTL |
| `width` | `inline-size` | Same in both directions |
| `height` | `block-size` | Same in both directions |

```css
/* Correct: logical properties */
.sidebar {
  margin-inline-start: 16px;
  padding-inline-end: 8px;
  border-inline-start: 2px solid var(--border-color);
  text-align: start;
}

/* Incorrect: physical properties */
.sidebar {
  margin-left: 16px;
  padding-right: 8px;
  border-left: 2px solid var(--border-color);
  text-align: left;
}
```

### 3.3 Bidirectional Text Handling

- All text containers must support both LTR and RTL text within the same paragraph.
- Use `dir="auto"` on elements that may contain mixed-direction text:
  ```html
  <p dir="auto">The command <code>git push</code> was successful.</p>
  ```
- Browsers automatically detect the direction of the first strong character.

### 3.4 Icon Direction

Icons must be direction-aware when they convey directional meaning:

| Icon Type | Flip in RTL | Example |
|-----------|-------------|---------|
| Navigation arrows (← →) | Yes | Back arrow flips |
| Forward/backward | Yes | History navigation |
| Progress indicators (left-to-right) | Yes | Progress bar fills right-to-left |
| Play/pause | No | Media controls stay same |
| Checkmark | No | Always same |
| Warning/error | No | Always same |
| Search magnifying glass | No | Always same |
| Settings gear | No | Always same |
| Close (×) | No | Always same |
| Expand/collapse chevrons | Yes | Chevron direction flips |

```css
/* RTL-aware arrow icon */
.icon-back {
  transform: scaleX(1);
}

[dir="rtl"] .icon-back {
  transform: scaleX(-1);
}
```

### 3.5 RTL Layout Implementation

```css
:root[dir="rtl"] {
  /* Mirror nav rail to right side */
  .nav-rail {
    order: 3;
  }

  /* Mirror sidebar to right side */
  .sidebar {
    order: 2;
    border-inline-start: none;
    border-inline-end: 1px solid var(--border-color);
  }

  /* Mirror right panel to left side */
  .right-panel {
    order: 0;
  }

  /* Scrollbars */
  .scrollable {
    direction: rtl;
  }
}
```

---

## 4. Language Switching

### 4.1 Switching Behavior

When the user changes the language in Settings:

1. **Immediate update**: All visible text updates within 500ms.
2. **No page reload**: React re-renders with new locale context.
3. **Preserve state**: All application state (open tabs, scroll position, form data) is preserved.
4. **Direction change**: If switching between LTR and RTL, layout mirrors with animation.
5. **Persistence**: Selected locale is stored in `localStorage` and restored on restart.

### 4.2 Language Detection

```
Priority order:
1. User's explicit choice in Settings
2. Electron app locale (OS setting)
3. Browser language (Electron default)
4. Fallback: en-US
```

### 4.3 Fallback Strategy

```
en-US (default)
  ├── en-GB → en-US (for missing keys)
  ├── de-DE → de → en-US
  ├── fr-FR → fr → en-US
  ├── ja-JP → ja → en-US
  ├── ar-SA → ar → en-US
  └── ...
```

Missing translations fall back to the base language, then to English.

---

## 5. Variable Text Length

### 5.1 Text Expansion Factors

| Language | Expansion Factor | Example: "Settings" |
|----------|-----------------|---------------------|
| English | 1.0× (baseline) | Settings |
| German | 1.3× | Einstellungen |
| French | 1.2× | Paramètres |
| Spanish | 1.2× | Configuración |
| Portuguese | 1.3× | Configurações |
| Japanese | 0.5× | 設定 |
| Chinese | 0.5× | 设置 |
| Korean | 0.7× | 설정 |
| Russian | 1.1× | Настройки |
| Arabic | 0.9× | الإعدادات |

### 5.2 Design for 200% Expansion

All containers must accommodate **200% text expansion** without breaking layout:

```css
/* Correct: flexible container */
.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  min-width: 0;
}

/* Correct: flexible button */
.button {
  padding-inline: 12px 16px;
  min-width: 0;
  max-width: 100%;
}

/* Incorrect: fixed width */
.nav-label {
  width: 120px;  /* Breaks with long text */
}
```

### 5.3 Truncation Strategy

When text exceeds available space:

1. **First**: Let container grow (up to max-width).
2. **Second**: Truncate with ellipsis (`text-overflow: ellipsis`).
3. **Third**: Show full text in tooltip on hover/focus.
4. **Never**: Wrap to an unexpected number of lines in UI controls.

```html
<button class="button" title="Full localized text here">
  <span class="button-label">Truncated text…</span>
</button>
```

### 5.4 Flexible Container Widths

```css
/* Use min/max instead of fixed widths */
.sidebar {
  width: clamp(200px, 20vw, 300px);
}

.dialog {
  width: min(640px, 90vw);
}

.form-label {
  width: auto;  /* Never fixed */
}
```

---

## 6. Unicode Support

### 6.1 Character Encoding

- All text is stored and transmitted as **UTF-8**.
- `meta charset="UTF-8"` is set in all HTML documents.
- Files are saved with UTF-8 encoding.
- No character encoding conversion is needed within the application.

### 6.2 Unicode Normalization

- Text input is normalized to **NFC** (Normalization Form C) for consistent comparison.
- Search is diacritic-insensitive by default (accent folding).
- Sorting follows locale-specific collation rules.

```typescript
const normalized = input.normalize('NFC');

// Diacritic-insensitive search
const matches = items.filter(item =>
  item.name.normalize('NFD').toLowerCase().includes(
    query.normalize('NFD').toLowerCase()
  )
);
```

### 6.3 Script Support

| Script | Rendering | Font Stack |
|--------|-----------|------------|
| Latin | Native | Segoe UI, SF Pro, system |
| CJK | Native | system-ui, "Microsoft YaHei", "Hiragino Sans" |
| Arabic | Native | Segoe UI, "Arabic Typesetting", system |
| Hebrew | Native | Segoe UI, "Arial Hebrew", system |
| Cyrillic | Native | Segoe UI, system |
| Devanagari | Via system font | Noto Sans Devanagari (fallback) |
| Thai | Via system font | Noto Sans Thai (fallback) |

---

## 7. Pluralization

### 7.1 CLDR Plural Rules

| Language | Plural Forms | Rules |
|----------|-------------|-------|
| English | one, other | `n = 1` → one, else other |
| German | one, other | `n = 1` → one, else other |
| French | one, other | `n = 0,1` → one, else other |
| Russian | one, few, many, other | Complex rules based on last digit and teen numbers |
| Arabic | zero, one, two, few, many, other | 6 forms based on n mod 100 |
| Japanese | other | Only one form |
| Chinese | other | Only one form |
| Korean | other | Only one form |

### 7.2 Translation Keys

```
// English
lessons_count: {
  one: "{{count}} lesson",
  other: "{{count}} lessons"
}

// Arabic (6 forms)
lessons_count: {
  zero: "٠ دروس",
  one: "درس واحد",
  two: "درسان",
  few: "{{count}} دروس",
  many: "{{count}} درسًا",
  other: "{{count}} درس"
}

// Russian (4 forms)
lessons_count: {
  one: "{{count}} урок",
  few: "{{count}} урока",
  many: "{{count}} уроков",
  other: "{{count}} урока"
}
```

### 7.3 Implementation

```typescript
function pluralize(count: number, translations: Record<string, string>): string {
  const rule = new Intl.PluralRules(currentLocale).select(count);
  return translations[rule].replace('{{count}}', String(count));
}
```

---

## 8. Localized Date and Time

### 8.1 Date Formatting

```typescript
const date = new Date(2026, 6, 19); // July 19, 2026

// Locale-aware formatting
new Intl.DateTimeFormat('en-US').format(date);   // "7/19/2026"
new Intl.DateTimeFormat('de-DE').format(date);   // "19.7.2026"
new Intl.DateTimeFormat('ja-JP').format(date);   // "2026/7/19"
new Intl.DateTimeFormat('ar-SA').format(date);   // "١٩‏/٧‏/٢٠٢٦"
```

### 8.2 Time Formatting

```typescript
const time = new Date(2026, 6, 19, 14, 30);

new Intl.DateTimeFormat('en-US', {
  hour: 'numeric',
  minute: '2-digit',
  hour12: true
}).format(time);  // "2:30 PM"

new Intl.DateTimeFormat('de-DE', {
  hour: 'numeric',
  minute: '2-digit',
  hour12: false
}).format(time);  // "14:30"
```

### 8.3 Relative Time

```typescript
new Intl.RelativeTimeFormat('en', { numeric: 'auto' }).format(-1, 'day');
// "yesterday"

new Intl.RelativeTimeFormat('de', { numeric: 'auto' }).format(-1, 'day');
// "gestern"

new Intl.RelativeTimeFormat('ja', { numeric: 'auto' }).format(-1, 'day');
// "昨日"
```

### 8.4 Calendar System

- Default: Gregorian calendar.
- Islamic calendar support available for Arabic locale.
- Japanese calendar (era) display optional.
- All date pickers respect locale calendar system.

---

## 9. Localized Numbers and Currency

### 9.1 Number Formatting

```typescript
const num = 1234567.89;

new Intl.NumberFormat('en-US').format(num);   // "1,234,567.89"
new Intl.NumberFormat('de-DE').format(num);   // "1.234.567,89"
new Intl.NumberFormat('fr-FR').format(num);   // "1 234 567,89"
new Intl.NumberFormat('ja-JP').format(num);   // "1,234,567.89"
```

### 9.2 Currency Formatting

```typescript
const price = 49.99;

new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD'
}).format(price);  // "$49.99"

new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR'
}).format(price);  // "49,99 €"

new Intl.NumberFormat('ja-JP', {
  style: 'currency',
  currency: 'JPY'
}).format(price);  // "￥50"
```

### 9.3 Percent Formatting

```typescript
const pct = 0.857;

new Intl.NumberFormat('en-US', {
  style: 'percent'
}).format(pct);  // "85.7%"

new Intl.NumberFormat('de-DE', {
  style: 'percent'
}).format(pct);  // "85,7 %"
```

---

## 10. Localized Keyboard Shortcuts

### 10.1 Shortcut Localization

Global shortcuts use **platform-standard modifiers**, not locale-specific ones:

| Platform | Modifier Key |
|----------|-------------|
| Windows | Ctrl |
| macOS | ⌘ (Cmd) |
| Linux | Ctrl |

### 10.2 Locale-Specific Considerations

- Keyboard shortcuts are **not** translated (Ctrl+K is always Ctrl+K).
- Display text adapts: "Ctrl+K" on Windows/Linux, "⌘K" on macOS.
- Some keyboard layouts may differ; shortcuts map to physical keys, not characters.
- Documentation shows shortcuts in locale-appropriate format.

---

## 11. Localization Testing

### 11.1 Pseudo-localization

Use pseudo-localization to test for:

- **String expansion**: Replace "a" with "áááá" to simulate 200% expansion.
- **Right-to-left**: Flip layout and verify mirroring.
- **Special characters**: Verify Unicode rendering.
- **Concatenation issues**: Detect hardcoded strings.

```typescript
// Pseudo-localization example
// "Settings" → "[!!!Şéťťíńĝś!!!]"
// "Save" → "[!!!Śávé!!!]"
```

### 11.2 Visual Review Checklist

| Check | Method |
|-------|--------|
| Text truncation | Review all screens in German (long strings) |
| Text overflow | Review all screens in Chinese (short strings) |
| RTL layout | Review all screens in Arabic |
| Date formatting | Check all date displays in multiple locales |
| Number formatting | Check all number displays in multiple locales |
| Icon direction | Verify RTL icon flipping |
| Form validation | Check error messages in all locales |
| Dialog sizing | Verify dialogs accommodate expanded text |

### 11.3 Pseudo-Locale Testing Configuration

```typescript
// Enable pseudo-locale in development
if (process.env.NODE_ENV === 'development') {
  enablePseudoLocale({
    strategy: 'expansion',  // Expand strings to 200%
    locale: 'en-X-pseudo',
    prefix: '[',
    suffix: ']',
  });
}
```

### 11.4 RTL Layout Verification Checklist

```
□ Sidebar appears on right side
□ Nav rail appears on right side
□ Right panel appears on left side
□ Text alignment is right-aligned
□ Scrollbar appears on left side
□ Icons flip where appropriate
□ Breadcrumbs read right-to-left
□ Back/forward arrows flip
□ Progress bars fill right-to-left
□ Form labels appear to the right of inputs
□ Dialogs open centered correctly
□ Tooltips appear on correct side
□ Context menus open on correct side
□ Focus order is reversed (right-to-left)
```

---

## 12. Translation File Structure

```
src/i18n/
├── en/
│   ├── common.json
│   ├── settings.json
│   ├── lessons.json
│   └── errors.json
├── de/
│   ├── common.json
│   ├── settings.json
│   ├── lessons.json
│   └── errors.json
├── ar/
│   ├── common.json
│   ├── settings.json
│   ├── lessons.json
│   └── errors.json
└── ...
```

### 12.1 Translation Key Structure

```json
{
  "nav": {
    "home": "Home",
    "lessons": "Lessons",
    "labs": "Labs",
    "settings": "Settings"
  },
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "confirm": "Confirm",
    "loading": "Loading..."
  },
  "lessons": {
    "count": {
      "one": "{{count}} lesson",
      "other": "{{count}} lessons"
    },
    "progress": "{{completed}} of {{total}} completed"
  },
  "errors": {
    "not_found": "Page not found",
    "network": "Network error. Please check your connection.",
    "save_failed": "Failed to save. Please try again."
  }
}
```

---

## 13. Implementation Guidelines

### 13.1 i18n Library

Use `react-intl` (FormatJS) for message formatting:

```typescript
import { useIntl } from 'react-intl';

function LessonCount({ count }: { count: number }) {
  const intl = useIntl();
  return (
    <p>
      {intl.formatMessage(
        { id: 'lessons.count', defaultMessage: '{count} lessons' },
        { count }
      )}
    </p>
  );
}
```

### 13.2 RTL Provider

```typescript
function RTLProvider({ children }: { children: React.ReactNode }) {
  const { locale } = useIntl();
  const isRTL = isRTLLocale(locale);

  return (
    <div dir={isRTL ? 'rtl' : 'ltr'} lang={locale}>
      {children}
    </div>
  );
}
```

### 13.3 Date/Time Component

```typescript
function FormattedDate({ date }: { date: Date }) {
  const intl = useIntl();
  return (
    <time dateTime={date.toISOString()}>
      {intl.formatDate(date, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })}
    </time>
  );
}
```

---

*Document version: 1.0.0 — Last updated: 2026-07-19*
