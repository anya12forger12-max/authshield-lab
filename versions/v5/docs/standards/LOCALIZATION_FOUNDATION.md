# AuthShield Lab — Localization Foundation

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab supports 10 languages with a JSON-based translation system, CLDR-compliant plural rules, locale-aware date/number formatting, and full right-to-left (RTL) support. The localization architecture prioritizes offline capability (all translations bundled), consistency (flat key structure), and completeness tracking.

---

## 2. Supported Languages

| Code | Language | Native Name | RTL | Status |
|------|----------|-------------|-----|--------|
| `en` | English | English | No | Complete (reference) |
| `te` | Telugu | తెలుగు | No | In progress |
| `hi` | Hindi | हिन्दी | No | In progress |
| `es` | Spanish | Español | No | Planned |
| `fr` | French | Français | No | Planned |
| `de` | German | Deutsch | No | Planned |
| `ja` | Japanese | 日本語 | No | Planned |
| `zh` | Chinese | 中文 | No | Planned |
| `ko` | Korean | 한국어 | No | Planned |
| `ar` | Arabic | العربية | Yes | Planned |

---

## 3. Translation File Structure

### 3.1 Directory Layout

```
translations/
├── en/
│   ├── messages.json        # Core translations
│   ├── assessment.json      # Assessment module
│   ├── auth.json            # Authentication module
│   ├── dashboard.json       # Dashboard module
│   ├── learning.json        # Learning engine
│   ├── plugin.json          # Plugin system
│   ├── report.json          # Reporting module
│   ├── settings.json        # Settings module
│   └── common.json          # Shared UI elements
├── te/
│   ├── messages.json
│   ├── assessment.json
│   └── ...
├── hi/
│   ├── messages.json
│   └── ...
└── _meta/
    ├── completeness.json    # Translation completeness scores
    └── keys.json            # Master key list
```

### 3.2 Flat Key Structure

All translation files use a flat key structure with dot-notation keys:

```json
{
  "dashboard.welcome.message": "Welcome back, {user_name}!",
  "dashboard.welcome.subtitle": "You have {count} pending assessments.",
  "dashboard.alerts.new": "New alert",
  "dashboard.alerts.new_count": "{count} new alerts",
  "dashboard.alerts.empty": "No alerts at this time.",
  "assessment.submit.button": "Submit Assessment",
  "assessment.submit.confirm": "Are you sure you want to submit?",
  "assessment.result.score": "Your score: {score}%",
  "assessment.result.pass": "You passed!",
  "assessment.result.fail": "You did not pass. Please try again.",
  "auth.login.username": "Username or email",
  "auth.login.password": "Password",
  "auth.login.submit": "Log in",
  "auth.login.forgot_password": "Forgot password?",
  "auth.login.error.invalid": "Invalid username or password.",
  "auth.login.error.locked": "Account locked. Try again in {minutes} minutes.",
  "common.button.save": "Save",
  "common.button.cancel": "Cancel",
  "common.button.submit": "Submit",
  "common.button.delete": "Delete",
  "common.button.confirm": "Confirm",
  "common.error.generic": "An error occurred. Please try again.",
  "common.error.not_found": "Resource not found.",
  "common.loading": "Loading...",
  "common.search.placeholder": "Search...",
  "common.nav.home": "Home",
  "common.nav.assessments": "Assessments",
  "common.nav.reports": "Reports",
  "common.nav.settings": "Settings",
  "common.nav.plugins": "Plugins",
  "common.nav.accessibility": "Accessibility"
}
```

### 3.3 Key Naming Convention

```
{module}.{feature}.{element}
```

| Segment | Description | Examples |
|---------|-------------|----------|
| **module** | Top-level module | `dashboard`, `assessment`, `auth`, `common` |
| **feature** | Feature within module | `welcome`, `submit`, `login`, `button` |
| **element** | UI element or message | `message`, `error`, `placeholder`, `tooltip` |

---

## 4. Translation Loading

### 4.1 Translator Implementation

```python
from authshield.localization_engine import Translator

translator = Translator(
    translation_dir=Path("translations"),
    default_locale="en",
    fallback_chain=["te", "hi", "en"],
    cache_translations=True,
)

# Translate a key
text = translator.translate(
    key="dashboard.welcome.message",
    locale="te",
    context={"user_name": "Alice"},
)
# "స్వాగతం, Alice!"
```

### 4.2 Fallback Chain

When a translation key is missing in the target locale:

```
1. Look up key in target locale (te)
2. If not found, look up in first fallback (hi)
3. If not found, look up in default locale (en)
4. If not found, return key itself (e.g., "dashboard.welcome.message")
```

### 4.3 Translation Loading Priority

```
translations/{locale}/{module}.json  →  Highest priority
translations/{locale}/messages.json  →  Fallback
translations/en/{module}.json        →  Default locale
translations/en/messages.json        →  Default fallback
```

---

## 5. Plural Rules

### 5.1 CLDR Plural Categories

| Locale | Categories | Example (count) |
|--------|------------|-----------------|
| English | one, other | 1 alert, 2 alerts |
| Telugu | one, other | 1 హెచ్చరిక, 2 హెచ్చరికలు |
| Hindi | one, other | 1 चेतावनी, 2 चेतावनियाँ |
| Arabic | zero, one, two, few, many, other | 0, 1, 2, 3-10, 11-99, 100+ |
| German | one, other | 1 Warnung, 2 Warnungen |
| Japanese | other | 1 アラート, 2 アラート |
| Chinese | other | 1 警报, 2 警报 |
| Korean | other | 1 경고, 2 경고 |

### 5.2 Plural Key Convention

```json
{
  "dashboard.alerts.count": {
    "one": "You have {count} alert.",
    "other": "You have {count} alerts."
  },
  "assessment.attempts.remaining": {
    "one": "You have {count} attempt remaining.",
    "other": "You have {count} attempts remaining."
  }
}
```

### 5.3 Plural Translation API

```python
from authshield.localization_engine import Translator

translator = Translator(...)

# Plural-aware translation
text = translator.translate_plural(
    key="dashboard.alerts.count",
    count=5,
    locale="en",
)
# "You have 5 alerts."

# Arabic (6 plural forms)
text = translator.translate_plural(
    key="dashboard.alerts.count",
    count=5,
    locale="ar",
)
# Uses "few" category for count 3-10

text = translator.translate_plural(
    key="dashboard.alerts.count",
    count=15,
    locale="ar",
)
# Uses "many" category for count 11-99
```

---

## 6. Date Formatting

### 6.1 Locale-Specific Formats

| Locale | Short | Medium | Long | Full |
|--------|-------|--------|------|------|
| **English** | 7/19/26 | Jul 19, 2026 | July 19, 2026 | Saturday, July 19, 2026 |
| **Telugu** | 19/7/26 | జూలై 19, 2026 | జూలై 19, 2026 | శనివారం, జూలై 19, 2026 |
| **Hindi** | 19/7/26 | 19 जुलाई 2026 | 19 जुलाई 2026 | शनिवार, 19 जुलाई 2026 |
| **German** | 19.07.26 | 19. Jul. 2026 | 19. Juli 2026 | Samstag, 19. Juli 2026 |
| **Japanese** | 2026/07/19 | 2026年7月19日 | 2026年7月19日 | 2026年7月19日土曜日 |
| **Chinese** | 2026/7/19 | 2026年7月19日 | 2026年7月19日 | 2026年7月19日星期六 |
| **Korean** | 2026. 7. 19. | 2026년 7월 19일 | 2026년 7월 19일 | 2026년 7월 19일 토요일 |
| **Arabic** | 19/7/2026 | 19 يوليو 2026 | 19 يوليو 2026 | السبت، 19 يوليو 2026 |

### 6.2 Time Formatting

| Locale | 12-hour | 24-hour |
|--------|---------|---------|
| **English** | 12:00 PM | 12:00 |
| **Telugu** | 12:00 PM | 12:00 |
| **Hindi** | 12:00 PM | 12:00 |
| **German** | 12:00 PM | 12:00 |
| **Japanese** | 午後12:00 | 12:00 |
| **Arabic** | 12:00 م | 12:00 |

### 6.3 Relative Time

| Locale | Example |
|--------|---------|
| **English** | "2 hours ago", "in 3 days" |
| **Telugu** | "2 గంటల క్రితం", "3 రోజుల్లో" |
| **Hindi** | "2 घंटे पहले", "3 दिनों में" |
| **German** | "vor 2 Stunden", "in 3 Tagen" |
| **Japanese** | "2時間前", "3日後" |

### 6.4 Date Formatting API

```python
from authshield.localization_engine import DateFormatter

df = DateFormatter()

# Locale-aware date formatting
formatted = df.format_date(
    date=datetime(2026, 7, 19),
    locale="te",
    style="long",
)
# "జూలై 19, 2026"

# Relative time
relative = df.format_relative(
    reference=datetime.now(),
    target=datetime.now() - timedelta(hours=2),
    locale="hi",
)
# "2 घंटे पहले"

# Time formatting
time_str = df.format_time(
    time=datetime(2026, 7, 19, 14, 30),
    locale="ja",
    format="24h",
)
# "14:30"
```

---

## 7. Number Formatting

### 7.1 Locale-Specific Number Formats

| Locale | Decimal | Grouping | Example (1234567.89) |
|--------|---------|----------|----------------------|
| **English** | . | , | 1,234,567.89 |
| **Telugu** | . | , | 12,34,567.89 (Indian) |
| **Hindi** | . | , | 12,34,567.89 (Indian) |
| **German** | , | . | 1.234.567,89 |
| **French** | , | \s | 1 234 567,89 |
| **Japanese** | . | , | 1,234,567.89 |
| **Chinese** | . | , | 1,234,567.89 |
| **Arabic** |٫ |٬ | ١٬٢٣٤٬٥٦٧٫٨٩ |

### 7.2 Currency Formatting

| Locale | Currency | Position | Example (42.50) |
|--------|----------|----------|-----------------|
| **English** | USD | Before | $42.50 |
| **Telugu** | INR | Before | ₹42.50 |
| **Hindi** | INR | Before | ₹42.50 |
| **German** | EUR | After | 42,50 € |
| **Japanese** | JPY | Before | ¥43 |
| **Arabic** | SAR | After | ٤٢٫٥٠ ر.س. |

### 7.3 Number Formatting API

```python
from authshield.localization_engine import NumberFormatter

nf = NumberFormatter()

# Number formatting
formatted = nf.format_number(
    number=1234567.89,
    locale="de",
)
# "1.234.567,89"

# Currency formatting
currency = nf.format_currency(
    amount=42.50,
    currency="EUR",
    locale="de",
)
# "42,50 €"

# Percentage formatting
percent = nf.format_percent(
    value=0.85,
    locale="te",
)
# "85%"

# Compact notation (1K, 1M, etc.)
compact = nf.format_compact(
    value=1500000,
    locale="en",
)
# "1.5M"
```

---

## 8. RTL Support

### 8.1 CSS Logical Properties

All layout uses CSS logical properties for automatic RTL support:

```css
/* Instead of: */
padding-left: 1rem;
margin-right: 0.5rem;
border-left: 2px solid;
text-align: left;

/* Use: */
padding-inline-start: 1rem;
margin-inline-end: 0.5rem;
border-inline-start: 2px solid;
text-align: start;
```

### 8.2 RTL Detection

```python
from authshield.localization_engine import RTLHelper

rtl = RTLHelper()

# Check if locale is RTL
is_rtl = rtl.is_rtl("ar")  # True
is_rtl = rtl.is_rtl("en")  # False

# Get CSS direction
direction = rtl.get_direction("ar")  # "rtl"
direction = rtl.get_direction("en")  # "ltr"

# Mirror layout properties
mirrored = rtl.mirror_css({
    "padding-left": "1rem",
    "margin-right": "0.5rem",
    "text-align": "left",
    "float": "left",
})
# {
#     "padding-right": "1rem",
#     "margin-left": "0.5rem",
#     "text-align": "right",
#     "float": "right",
# }
```

### 8.3 Layout Mirroring

```tsx
// React component with RTL support
import { useRTL } from "@authshield/localization";

function Sidebar() {
  const { direction, logicalProps } = useRTL();

  return (
    <aside
      dir={direction}
      style={{
        [logicalProps("padding-inline-start")]: "1rem",
        [logicalProps("margin-inline-end")]: "0.5rem",
      }}
    >
      {/* Content */}
    </aside>
  );
}
```

---

## 9. Translation Validation

### 9.1 Completeness Scoring

```python
from authshield.localization_engine import CompletenessChecker

checker = CompletenessChecker(
    translation_dir=Path("translations"),
    master_key_file=Path("translations/_meta/keys.json"),
)

# Check completeness for a locale
score = checker.check_locale("te")
# CompletenessScore(
#     total_keys=500,
#     translated_keys=450,
#     missing_keys=50,
#     percentage=90.0,
#     incomplete_modules={
#         "assessment": {"translated": 80, "total": 100, "percentage": 80.0},
#         "learning": {"translated": 40, "total": 60, "percentage": 66.7},
#     },
# )

# Get missing keys
missing = checker.get_missing_keys("te")
# [
#     {"key": "assessment.rubric.title", "module": "assessment"},
#     {"key": "learning.spaced_repetition.label", "module": "learning"},
#     ...
# ]

# Get all locales completeness
all_scores = checker.check_all_locales()
# {
#     "en": {"percentage": 100.0, "total": 500, "translated": 500},
#     "te": {"percentage": 90.0, "total": 500, "translated": 450},
#     "hi": {"percentage": 75.0, "total": 500, "translated": 375},
#     ...
# }
```

### 9.2 Key Consistency Validation

```python
# Validate key consistency across locales
issues = checker.validate_consistency()
# [
#     {"type": "missing_in_locale", "key": "new.feature.label", "locale": "te"},
#     {"type": "extra_in_locale", "key": "old.feature.label", "locale": "hi"},
#     {"type": "type_mismatch", "key": "count.value", "locale": "de",
#      "expected": "plural", "actual": "string"},
# ]
```

### 9.3 Placeholder Validation

```python
# Validate that placeholders match between source and translation
issues = checker.validate_placeholders("te")
# [
#     {
#         "key": "dashboard.welcome.message",
#         "issue": "missing_placeholder",
#         "expected": "{user_name}",
#         "actual": "Welcome back!",
#     },
# ]
```

---

## 10. Translation Workflow

### 10.1 Adding a New Key

```python
# 1. Add key to English reference file
# translations/en/dashboard.json
{
  "dashboard.new_feature.label": "New Feature"
}

# 2. Add to master key list
# translations/_meta/keys.json
{
  "keys": ["dashboard.new_feature.label"],
  "modules": {"dashboard": ["new_feature.label"]}
}

# 3. Update completeness scores
checker.update_completeness()

# 4. Mark for translation in other locales
checker.mark_for_translation("dashboard.new_feature.label")
```

### 10.2 Translation Process

```
1. English key added to translations/en/*.json
2. Master key list updated
3. Completeness checker flags key as missing in other locales
4. Translators provide translations for each locale
5. Translations added to translations/{locale}/*.json
6. Completeness checker verifies:
   - Key exists in locale file
   - Plural forms are correct
   - Placeholders match
   - No extra keys
7. Completeness scores updated
8. Build includes updated translations
```

---

## 11. Offline Considerations

| Aspect | Implementation |
|--------|---------------|
| **Translation files** | Bundled in application; no network required |
| **Locale detection** | Browser/OS locale detection; user preference storage |
| **Fallback** | English fallback built-in; no network needed for fallback |
| **Updates** | Translation updates via application updates (not real-time) |
| **Size** | Each locale ~50-100KB; total for 10 locales ~1MB |
| **Loading** | Lazy loading per module; only load needed locale |

---

## 12. File Format Specification

### 12.1 Translation File Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": {
    "oneOf": [
      { "type": "string" },
      {
        "type": "object",
        "properties": {
          "one": { "type": "string" },
          "other": { "type": "string" },
          "few": { "type": "string" },
          "many": { "type": "string" },
          "zero": { "type": "string" }
        },
        "required": ["other"]
      }
    ]
  }
}
```

### 12.2 Message Format (ICU-inspired)

```json
{
  "greeting": "Hello, {name}!",
  "items": {
    "one": "You have {count} item.",
    "other": "You have {count} items."
  },
  "notification": "You have {count, plural, one {# notification} other {# notifications}}."
}
```

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
