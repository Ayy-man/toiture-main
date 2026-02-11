---
phase: 27-ai-chat-interface
plan: 02
subsystem: frontend-chat-ui
tags: [ui-components, chat-interface, mobile-first, i18n]
dependency_graph:
  requires: [admin-layout, shadcn-ui, i18n-system]
  provides: [chat-ui-components, chat-page-route, chat-nav-item]
  affects: [sidebar-navigation, admin-routes]
tech_stack:
  added: []
  patterns: [local-state-management, auto-scroll, auto-resize-textarea, mock-data]
key_files:
  created:
    - frontend/src/components/chat/chat-message.tsx
    - frontend/src/components/chat/chat-input.tsx
    - frontend/src/components/chat/suggestion-pills.tsx
    - frontend/src/components/chat/chat-typing-indicator.tsx
    - frontend/src/components/chat/chat-container.tsx
    - frontend/src/app/(admin)/chat/page.tsx
  modified:
    - frontend/src/components/admin/app-sidebar.tsx
    - frontend/src/lib/i18n/fr.ts
    - frontend/src/lib/i18n/en.ts
    - frontend/src/app/(admin)/layout.tsx
decisions:
  - title: "Local state only (no API calls)"
    rationale: "Plan 02 focuses on UI shell. API integration happens in Plan 03."
  - title: "MessageCircle icon for chat nav"
    rationale: "Distinguishes chat from retours (MessageSquare). Different visual identity."
  - title: "Chat as second sidebar item"
    rationale: "Steven uses chat frequently from mobile, needs prominent position after Estimateur."
  - title: "Auto-resizing textarea without shadcn Textarea"
    rationale: "Need direct ref control for scrollHeight-based auto-resize behavior."
  - title: "Hide scrollbar but keep scroll on pills"
    rationale: "Cleaner UI on mobile while preserving horizontal scroll functionality."
metrics:
  duration: "3m 26s"
  tasks_completed: 2
  components_created: 5
  files_modified: 4
  translation_keys_added: 18
completed_date: 2026-02-12
---

# Phase 27 Plan 02: Chat UI Components and Page Summary

**All frontend chat UI components built and integrated into /chat route. Mobile-first design with local state management for development and testing.**

## What Was Built

### Task 1: Chat UI Components (4 components)

**ChatMessage** (`frontend/src/components/chat/chat-message.tsx`)
- User and assistant message bubbles with distinct styling
- User: right-aligned, primary background, rounded-br-md corner
- Assistant: left-aligned, muted background, rounded-bl-md corner
- Avatar icons (User/Bot from lucide-react)
- Timestamp display below message
- Basic markdown support (bold with `**text**`)
- Mobile-responsive: max-w-[85%] on mobile, max-w-[70%] on desktop

**ChatInput** (`frontend/src/components/chat/chat-input.tsx`)
- Auto-resizing textarea (1 row → 4 rows max, then scrolls)
- Direct textarea element (not shadcn component) for ref control
- Send button with Send icon from lucide-react
- Enter to send, Shift+Enter for newline
- Loading state with spinner
- `enterkeyhint="send"` for mobile keyboards
- Border rounded-xl wrapper with flex layout

**SuggestionPills** (`frontend/src/components/chat/suggestion-pills.tsx`)
- Horizontal scrollable flex row (overflow-x-auto)
- shadcn Badge variant="outline" with rounded-full styling
- Hover effect: bg-primary + text-primary-foreground transition
- Hidden scrollbar but preserved scroll functionality
- Returns null when suggestions array is empty
- Disabled state support

**ChatTypingIndicator** (`frontend/src/components/chat/chat-typing-indicator.tsx`)
- Three bouncing dots animation with staggered delays (0s, 0.15s, 0.3s)
- Muted bubble styling matching assistant messages
- Bot icon avatar for consistency
- CSS-only animation using animate-bounce
- Conditional rendering based on `visible` prop

### Task 2: ChatContainer, Page, Navigation, and i18n

**ChatContainer** (`frontend/src/components/chat/chat-container.tsx`)
- Full-height layout: `h-[calc(100vh-4rem)]` (minus admin header)
- Three-section structure:
  - Fixed header: title + session state badge + "New Chat" button (RotateCcw icon)
  - Scrollable message list with auto-scroll via useRef + scrollIntoView
  - Fixed bottom: suggestion pills + input area
- Local state management (no API calls):
  - `messages`: Array of Message objects with id/role/content/timestamp
  - `suggestions`: String array for quick-reply chips
  - `isLoading`: Boolean for typing indicator
  - `sessionState`: String tracking conversation state
- Mock behavior:
  - Initial greeting message from i18n
  - 1-second timeout for mock assistant replies
  - Dynamic suggestions that update after each interaction
- Auto-scroll: useEffect triggers scrollIntoView when messages array changes
- Message type exported for reuse in Plan 03

**Chat Page Route** (`frontend/src/app/(admin)/chat/page.tsx`)
- Simple "use client" page rendering `<ChatContainer />`
- No additional metadata (admin layout handles breadcrumbs)

**Sidebar Navigation** (`frontend/src/components/admin/app-sidebar.tsx`)
- Chat nav item added as **second item** (after Estimateur, before Historique)
- Icon: `MessageCircle` from lucide-react (distinct from retours' MessageSquare)
- Uses `t.nav.chat` for bilingual label

**i18n Translations** (18 new keys in `frontend/src/lib/i18n/fr.ts` and `en.ts`)
- `nav.chat`: "Chat" (FR) / "Chat" (EN)
- `chat.title`: "Chat Cortex" / "Cortex Chat"
- `chat.newChat`: "Nouveau chat" / "New chat"
- `chat.placeholder`: "Decrivez le projet de toiture..." / "Describe the roofing project..."
- `chat.greeting`: Full greeting with example (bilingual, sqft vs pi2)
- `chat.sessionState`: "Etat de la session" / "Session state"
- Plus 12 additional keys for future features (generateQuote, selectTier, createSubmission, etc.)

**Admin Layout** (`frontend/src/app/(admin)/layout.tsx`)
- Added `chat: t.nav.chat` to routeLabels for breadcrumb support

## Deviations from Plan

None - plan executed exactly as written.

## Testing Notes

**Manual testing required:**
1. Navigate to /chat in browser
2. Verify chat sidebar item visible with MessageCircle icon
3. Greeting message appears on load
4. Type message and press Enter → user bubble appears on right
5. Mock assistant reply appears after 1 second with typing indicator
6. Suggestion pills render below messages and are clickable
7. Auto-scroll works when messages overflow viewport
8. Input auto-resizes when typing multi-line messages (up to 4 rows)
9. "New Chat" button resets conversation
10. Language toggle switches greeting and placeholder text

**Expected behavior:**
- All chat components render correctly on mobile viewport (375px width)
- Chat layout uses full available height with fixed header and input
- Messages display as distinct user/assistant bubbles
- Input handles Enter to send and Shift+Enter for newlines
- Suggestion pills are horizontally scrollable without visible scrollbar

## Architecture Notes

**Local State Pattern:**
This plan intentionally uses local state with mock data to enable UI development and testing independently of the backend. Plan 03 will replace the mock behavior with actual API integration to the backend chat session service.

**Auto-Scroll Implementation:**
Uses a `messagesEndRef` (created with useRef) positioned at the end of the message list. A useEffect watches `messages.length` and triggers `scrollIntoView({ behavior: "smooth" })` whenever new messages are added.

**Auto-Resize Textarea:**
Direct textarea element (not shadcn Textarea component) allows ref-based height control. On input change, useEffect sets height to "auto" then to `scrollHeight`, capped at 128px (max-h-32 = 4 rows).

**Mobile-First Design:**
- Full viewport height layout
- Touch-friendly suggestion pills
- `enterkeyhint="send"` attribute for mobile keyboard optimization
- Responsive message bubble widths (85% mobile, 70% desktop)

## Performance Considerations

- Suggestion pills use hidden scrollbar CSS for cleaner mobile UX
- Auto-scroll uses `behavior: "smooth"` for better perceived performance
- Typing indicator uses CSS-only animation (no JavaScript interval)
- Mock timeout at 1 second provides realistic chat latency simulation

## Next Steps (Plan 03)

1. Backend API integration for chat session management
2. Replace mock timeout with actual POST to `/chat/send` endpoint
3. Field extraction from conversation messages
4. Quote generation trigger when conversation complete
5. Submission creation flow from chat context

## Self-Check: PASSED

**Created files exist:**
```bash
FOUND: frontend/src/components/chat/chat-message.tsx
FOUND: frontend/src/components/chat/chat-input.tsx
FOUND: frontend/src/components/chat/suggestion-pills.tsx
FOUND: frontend/src/components/chat/chat-typing-indicator.tsx
FOUND: frontend/src/components/chat/chat-container.tsx
FOUND: frontend/src/app/(admin)/chat/page.tsx
```

**Commits exist:**
```bash
FOUND: 675bc77 (Task 1: Chat UI components)
FOUND: 99b709a (Task 2: ChatContainer and page integration)
```

**TypeScript compilation:** No errors in chat component files.

**i18n keys present:** Both fr.ts and en.ts contain chat section with 18 keys.
