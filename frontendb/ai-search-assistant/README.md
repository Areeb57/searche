# Meridian — AI Search Assistant

A production-quality AI chat/search frontend built with **Next.js 16 + React**, plain CSS Modules, and zero UI framework dependencies.

## Quick Start

```bash
npm install
npm run dev
# → http://localhost:3000
```

## Stack

| Layer | Choice |
|-------|--------|
| Framework | Next.js 16 (App Router) |
| UI | React 18 |
| Styling | Plain CSS Modules + CSS variables |
| Icons | Lucide React |
| State | React Context + useReducer |
| Persistence | localStorage |

## Features

- **Sidebar** with grouped chat history (Today / Yesterday / Older), rename, delete, 3-dot menus
- **Header** with model selector dropdown and user menu
- **Chat window** with markdown rendering — bold, italic, code blocks, lists, tables, blockquotes, links
- **Streaming animation** — AI responses stream in character-by-character
- **Typing indicator** with animated dots
- **Search progress** component (expandable, step-by-step)
- **Source cards** with favicon, domain, description and hover state
- **Message actions** — copy to clipboard, thumbs up/down, regenerate
- **Empty state** with clickable suggestion cards
- **Settings modal** — light/dark/system theme, enter-to-send, timestamps, compact mode, auto-scroll
- **Dark mode** — full CSS variable system, no flash on load
- **Responsive** — mobile sidebar drawer with overlay, touch-friendly
- **Accessible** — semantic HTML, keyboard navigation, ARIA labels, visible focus

## Project Structure

```
app/
  layout.jsx          # Root layout + theme flash prevention
  page.jsx            # Main chat page + streaming logic
  globals.css         # CSS variables (light + dark), reset, layout

components/
  Sidebar/            # Sidebar, chat history, item menus
  Header/             # Sticky header, model selector, user menu
  Chat/               # ChatWindow, Message, TypingIndicator, EmptyState
  Input/              # MessageInput with auto-resize
  Search/             # SearchProgress, SearchResults, SourceCard
  Settings/           # SettingsModal with toggles

contexts/
  AppContext.js       # Global state (chats, messages, settings, theme)

lib/
  api.js              # Mock API layer + 5 sample conversations
  markdown.js         # Lightweight markdown → HTML renderer
```

## Connecting a Real Backend

All API calls are isolated in `lib/api.js`. Replace the mock functions:

```js
// Currently returns mock data:
export async function sendMessage(chatId, message) { ... }
export async function createChat() { ... }
export async function deleteChat(chatId) { ... }
export async function renameChat(chatId, newTitle) { ... }
export async function getChat(chatId) { ... }
```

For streaming, replace the character-by-character simulation in `app/page.jsx`
with a real `ReadableStream` / `EventSource` consumer.

## License

MIT
