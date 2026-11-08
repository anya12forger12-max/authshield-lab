# Motion System — AuthShield Lab

> Principles, guidelines, and specifications for all animation and motion in the interface.

---

## Motion Philosophy

Motion in AuthShield Lab serves three purposes:

1. **Feedback** — confirm that an action was recognized and processed
2. **Orientation** — help users understand where content came from and where it went
3. **Focus** — guide attention to important changes

Motion is never decorative. Every animation must serve a functional purpose. All animations are optional via `prefers-reduced-motion`.

---

## Timing Tokens

### Duration Scale

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| Duration Instant | `--duration-instant` | 0ms | Immediate state changes |
| Duration Micro | `--duration-micro` | 50ms | Opacity changes, color shifts |
| Duration Fast | `--duration-fast` | 100ms | Hover states, focus rings, tooltips |
| Duration Normal | `--duration-normal` | 200ms | Standard transitions, dropdowns |
| Duration Slow | `--duration-slow` | 300ms | Page transitions, panel expand/collapse |
| Duration Slower | `--duration-slower` | 500ms | Complex multi-element animations |
| Duration Slowest | `--duration-slowest` | 700ms | Choreographed entrance sequences |

### Timing Selection Guide

```
Micro (50ms):   Color changes, opacity shifts
Fast (100ms):   Hover effects, focus indicators, toggles
Normal (200ms): Dropdowns, tooltips, small reveals
Slow (300ms):   Panel transitions, modal entrance, page fades
Slower (500ms): Multi-step animations, complex entrances
Slowest (700ms): Onboarding sequences, celebrations
```

---

## Easing Tokens

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| Easing Default | `--easing-default` | cubic-bezier(0.4, 0, 0.2, 1) | General purpose |
| Easing Enter | `--easing-enter` | cubic-bezier(0, 0, 0.2, 1) | Elements appearing |
| Easing Exit | `--easing-exit` | cubic-bezier(0.4, 0, 1, 1) | Elements disappearing |
| Easing Move | `--easing-move` | cubic-bezier(0.4, 0, 0.2, 1) | Elements repositioning |
| Easing Spring | `--easing-spring` | cubic-bezier(0.34, 1.56, 0.64, 1) | Playful, bouncy (use sparingly) |

### Easing Selection Guide

```
Enter (ease-out):    Elements appear — start fast, decelerate to rest
Exit (ease-in):      Elements disappear — accelerate from rest, end fast
Move (ease-in-out):  Elements reposition — smooth acceleration and deceleration
Spring:              Celebration moments — playful overshoot and settle
```

---

## Transition Specifications

### Page Transitions

| Transition | Duration | Easing | Properties |
|---|---|---|---|
| Page fade | 200ms | enter/exit | opacity |
| Page crossfade | 300ms | default | opacity |
| Section change | 200ms | enter | opacity, transform: translateY(4px → 0) |

**Implementation:**
```css
.page-enter {
  opacity: 0;
}
.page-enter-active {
  opacity: 1;
  transition: opacity 200ms var(--easing-enter);
}
.page-exit {
  opacity: 1;
}
.page-exit-active {
  opacity: 0;
  transition: opacity 150ms var(--easing-exit);
}
```

### Component Transitions

| Component | Transition | Duration | Easing |
|---|---|---|---|
| Dropdown open | Fade + scale | 200ms | enter |
| Dropdown close | Fade | 150ms | exit |
| Modal open | Fade + scale | 200ms | enter |
| Modal close | Fade | 150ms | exit |
| Tooltip show | Fade | 100ms | enter |
| Tooltip hide | Fade | 75ms | exit |
| Toast enter | Slide + fade | 300ms | enter |
| Toast exit | Slide + fade | 200ms | exit |
| Tab indicator | Slide | 200ms | move |
| Accordion expand | Height | 200ms | default |
| Sidebar resize | Width | 200ms | move |
| Button press | Scale | 100ms | default |

### Panel Transitions

| Panel | Transition | Duration | Easing |
|---|---|---|---|
| Sidebar expand | Width | 200ms | move |
| Sidebar collapse | Width | 200ms | move |
| Right panel show | Width + opacity | 200ms | enter |
| Right panel hide | Width + opacity | 200ms | exit |
| Split pane resize | Width/Height | 0ms (instant) | — |

---

## Loading Indicators

### Spinner

**Usage**: Inline loading for buttons, small operations

| Property | Value |
|---|---|
| Size | 16px (sm), 20px (md), 24px (lg) |
| Color | current text color |
| Animation | 360deg rotation, 900ms duration, linear easing |
| Stroke | 2px, round linecap |

### Skeleton Screens

**Usage**: Content area loading — shows expected layout shape

| Property | Value |
|---|---|
| Animation | Shimmer effect, left-to-right gradient |
| Duration | 1500ms, infinite |
| Easing | ease-in-out |
| Base color | gray-200 (light), gray-700 (dark) |
| Shimmer color | gray-100 (light), gray-600 (dark) |

**Skeleton shapes:**
- Text: Rectangle, 100% width, 14px height, 4px border-radius
- Heading: Rectangle, 60% width, 20px height, 4px border-radius
- Avatar: Circle, 40x40px
- Card: Rectangle, 100% width, 200px height, 8px border-radius
- Image: Rectangle, 100% width, 160px height, 8px border-radius

### Progress Bar

**Usage**: Known-duration operations

| Property | Value |
|---|---|
| Height | 4px (compact), 8px (standard), 12px (prominent) |
| Border-radius | 9999px (full) |
| Fill color | blue-500 |
| Background | gray-200 (light), gray-700 (dark) |
| Animation | Width transition, 300ms, ease-in-out |
| Stripe animation (indeterminate) | 1000ms linear, background-position |

### Indeterminate Progress

**Usage**: Unknown-duration operations

| Property | Value |
|---|---|
| Type | Bar or spinner |
| Bar animation | Width oscillates 0% → 100%, 1500ms, ease-in-out |
| Bar transform | translateX(-100%) → translateX(100%) |

---

## Focus Animation

### Focus Ring Appearance

| Property | Value |
|---|---|
| Duration | 0ms (instant on keyboard) |
| Transition | box-shadow 100ms var(--easing-fast) |
| Ring style | 2px solid blue-500 |
| Ring offset | 2px |

### Focus Movement

When focus moves to a new element (especially after keyboard navigation):

| Property | Value |
|---|---|
| Duration | 0ms for keyboard navigation |
| Transition | Never animate focus position for keyboard users |
| Exception | Smooth scroll to focused element (300ms) when off-screen |

**Rule**: Focus indicators appear instantly. Never delay focus ring appearance with animation.

---

## Notification Animation

### Toast Entrance

```
Start: transform: translateX(100%), opacity: 0
End:   transform: translateX(0), opacity: 1
Duration: 300ms
Easing: enter
```

### Toast Exit

```
Start: transform: translateX(0), opacity: 1
End:   transform: translateX(100%), opacity: 0
Duration: 200ms
Easing: exit
```

### Notification Badge Pop

```
Start: transform: scale(0)
End:   transform: scale(1)
Duration: 200ms
Easing: spring
```

---

## Panel Animation

### Collapse/Expand

**Accordion, Sidebar, Collapsible sections:**

| Property | Value |
|---|---|
| Expand | height: 0 → auto, opacity: 0 → 1 |
| Collapse | height: auto → 0, opacity: 1 → 0 |
| Duration | 200ms |
| Easing | default |
| Overflow | hidden during animation |

**Implementation:**
```css
.collapsible-enter {
  height: 0;
  opacity: 0;
  overflow: hidden;
}
.collapsible-enter-active {
  height: var(--collapsible-height);
  opacity: 1;
  transition: height 200ms var(--easing-default), opacity 200ms var(--easing-default);
}
```

---

## Reduced Motion

### Respect for User Preferences

All animations are optional. The application respects `prefers-reduced-motion` and provides a manual override in Settings > Accessibility.

### Reduced Motion Behavior

| Animation | Normal | Reduced |
|---|---|---|
| Page transitions | Fade/slide | Instant (no transition) |
| Component transitions | Fade/scale | Instant (no transition) |
| Loading spinners | Spinning | Static (opacity pulse or no animation) |
| Progress bars | Smooth fill | Instant update |
| Skeleton shimmer | Shimmer animation | Static |
| Toast entrance | Slide in | Fade in (200ms) |
| Focus ring | Instant | Instant |
| Celebrations | Animated | Static badge only |
| Panel resize | Smooth | Instant |

### Implementation

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Manual override */
[data-reduced-motion="true"] {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Performance Budget

### Rules

1. **60fps minimum** — no animation may drop below 60 frames per second
2. **GPU-accelerated properties only** — animate only `transform` and `opacity`
3. **No layout thrashing** — never animate `width`, `height`, `margin`, `padding`, `top`, `left`
4. **Will-change hint** — use `will-change: transform` or `will-change: opacity` for anticipated animations
5. **No simultaneous animations** — maximum 3 animated elements at any time
6. **No jank on scroll** — scroll-linked animations are forbidden

### Animated Properties (Allowed)

| Property | GPU-Accelerated | Usage |
|---|---|---|
| transform | Yes | Position, scale, rotate |
| opacity | Yes | Fade in/out |
| will-change | Yes (hint only) | Pre-allocate GPU layer |

### Animated Properties (Forbidden for Animation)

| Property | Reason | Alternative |
|---|---|---|
| width/height | Triggers layout | Use transform: scale() |
| top/left/right/bottom | Triggers layout | Use transform: translate() |
| margin/padding | Triggers layout | Use transform: translate() |
| border-width | Triggers layout | Use transform: scale() |
| font-size | Triggers layout | Use transform: scale() |
| box-shadow | Expensive repaint | Use pseudo-element or opacity |
| filter | Expensive on some GPUs | Use opacity |

### Exception: Height Animations

Height animations (accordion expand/collapse) are acceptable when:
- Using `max-height` or CSS `grid` row transitions
- The element has `overflow: hidden`
- The animation duration is ≤ 300ms
- The element does not contain complex child layouts

---

## Animation Testing

### Checklist

- [ ] All animations work at 60fps (use Chrome DevTools Performance panel)
- [ ] `prefers-reduced-motion` disables all animations
- [ ] Manual "Reduce motion" setting in Settings > Accessibility works
- [ ] No animations trigger on page load (only on user interaction)
- [ ] Animations are smooth on low-end hardware (integrated graphics)
- [ ] No animation causes content to be temporarily unreadable
- [ ] Focus indicators are always visible regardless of animation state
- [ ] Screen reader announces all dynamic content changes regardless of animation

### Performance Testing

```
1. Open Chrome DevTools > Performance
2. Enable "Screenshots" and "Paint flashing"
3. Perform the animated action
4. Verify:
   - Frame rate stays above 55fps
   - No red (long) frames
   - No layout shifts (green bars in Layout column)
   - GPU activity is smooth (no spikes)
```

---

## Celebration Animations

Used sparingly for significant achievements (course completion, certification earned, streak milestones).

| Animation | Trigger | Duration | Reduced Motion Alternative |
|---|---|---|---|
| Confetti | Course completion | 3000ms | Static "Congratulations" badge |
| Progress fill | Module complete | 1000ms | Instant 100% state |
| Badge unlock | Achievement earned | 500ms | Static badge appearance |
| Streak counter | Daily streak increment | 300ms | Number change (no animation) |

### Celebration Rules

- Maximum 1 celebration animation per session
- Never interrupt ongoing user work with celebrations
- Show celebration at a natural stopping point (after page load, not during typing)
- Always dismissable (Escape key)
- Respect reduced motion preference

---

*Motion should make the interface feel alive and responsive, never distracting or overwhelming. When in doubt, use less motion.*
