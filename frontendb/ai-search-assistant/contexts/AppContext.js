'use client';

import { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { MOCK_CONVERSATIONS, generateId, groupChatsByDate } from '@/lib/api';

const initialSettings = {
  theme: 'system',
  enterToSend: true,
  showTimestamps: false,
  autoScroll: true,
  compactMode: false,
};

const initialState = {
  chats: [],
  currentChatId: null,
  sidebarOpen: false,
  isLoading: false,
  settings: initialSettings,
  hydrated: false,
};

function reducer(state, action) {
  switch (action.type) {

    case 'HYDRATE':
      return { ...state, ...action.payload, hydrated: true };

    case 'ADD_CHAT':
      return {
        ...state,
        chats: [action.payload, ...state.chats],
        currentChatId: action.payload.id,
      };

    case 'SET_CURRENT_CHAT':
      return { ...state, currentChatId: action.payload };

    case 'DELETE_CHAT': {
      const remaining = state.chats.filter(c => c.id !== action.payload);
      return {
        ...state,
        chats: remaining,
        currentChatId:
          state.currentChatId === action.payload
            ? (remaining[0]?.id ?? null)
            : state.currentChatId,
      };
    }

    case 'RENAME_CHAT':
      return {
        ...state,
        chats: state.chats.map(c =>
          c.id === action.payload.id ? { ...c, title: action.payload.title } : c
        ),
      };

    case 'ADD_MESSAGE':
      return {
        ...state,
        chats: state.chats.map(c =>
          c.id === action.payload.chatId
            ? { ...c, messages: [...c.messages, action.payload.message] }
            : c
        ),
      };

    case 'UPDATE_MESSAGE_CONTENT':
      return {
        ...state,
        chats: state.chats.map(c =>
          c.id === action.payload.chatId
            ? {
                ...c,
                messages: c.messages.map(m =>
                  m.id === action.payload.messageId
                    ? { ...m, content: action.payload.content }
                    : m
                ),
              }
            : c
        ),
      };

    case 'UPDATE_CHAT_TITLE':
      return {
        ...state,
        chats: state.chats.map(c =>
          c.id === action.payload.chatId ? { ...c, title: action.payload.title } : c
        ),
      };

    case 'SET_SIDEBAR':
      return { ...state, sidebarOpen: action.payload };

    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarOpen: !state.sidebarOpen };

    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'SET_SETTINGS':
      return { ...state, settings: { ...state.settings, ...action.payload } };

    default:
      return state;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  // ── Hydrate from localStorage once on mount ──────────────────
  useEffect(() => {
    let chats = MOCK_CONVERSATIONS;
    let settings = initialSettings;
    let currentChatId = null;

    try {
      const raw = localStorage.getItem('meridian-chats');
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) chats = parsed;
      }
    } catch (_) {}

    try {
      const raw = localStorage.getItem('meridian-settings');
      if (raw) settings = { ...initialSettings, ...JSON.parse(raw) };
    } catch (_) {}

    try {
      const raw = localStorage.getItem('meridian-current');
      if (raw) currentChatId = raw;
    } catch (_) {}

    if (!currentChatId || !chats.find(c => c.id === currentChatId)) {
      currentChatId = chats[0]?.id ?? null;
    }

    dispatch({ type: 'HYDRATE', payload: { chats, settings, currentChatId } });
    applyTheme(settings.theme);
  }, []);

  // ── Persist chats ────────────────────────────────────────────
  useEffect(() => {
    if (!state.hydrated) return;
    try { localStorage.setItem('meridian-chats', JSON.stringify(state.chats)); } catch (_) {}
  }, [state.chats, state.hydrated]);

  // ── Persist settings & apply theme ──────────────────────────
  useEffect(() => {
    if (!state.hydrated) return;
    try { localStorage.setItem('meridian-settings', JSON.stringify(state.settings)); } catch (_) {}
    applyTheme(state.settings.theme);
  }, [state.settings, state.hydrated]);

  // ── Persist current chat ─────────────────────────────────────
  useEffect(() => {
    if (!state.hydrated || !state.currentChatId) return;
    try { localStorage.setItem('meridian-current', state.currentChatId); } catch (_) {}
  }, [state.currentChatId, state.hydrated]);

  // ── Derived ──────────────────────────────────────────────────
  const currentChat = state.chats.find(c => c.id === state.currentChatId) ?? null;
  const chatGroups = groupChatsByDate(state.chats);

  // ── Actions ──────────────────────────────────────────────────
  const createNewChat = useCallback(() => {
    const chat = {
      id: generateId('chat'),
      title: 'New conversation',
      createdAt: new Date().toISOString(),
      messages: [],
    };
    dispatch({ type: 'ADD_CHAT', payload: chat });
    dispatch({ type: 'SET_SIDEBAR', payload: false });
    return chat;
  }, []);

  const selectChat = useCallback((id) => {
    dispatch({ type: 'SET_CURRENT_CHAT', payload: id });
    dispatch({ type: 'SET_SIDEBAR', payload: false });
  }, []);

  const deleteChat = useCallback((id) => {
    dispatch({ type: 'DELETE_CHAT', payload: id });
  }, []);

  const renameChat = useCallback((id, title) => {
    dispatch({ type: 'RENAME_CHAT', payload: { id, title } });
  }, []);

  const addMessage = useCallback((chatId, message) => {
    dispatch({ type: 'ADD_MESSAGE', payload: { chatId, message } });
  }, []);

  const updateMessageContent = useCallback((chatId, messageId, content) => {
    dispatch({ type: 'UPDATE_MESSAGE_CONTENT', payload: { chatId, messageId, content } });
  }, []);

  const updateChatTitle = useCallback((chatId, title) => {
    dispatch({ type: 'UPDATE_CHAT_TITLE', payload: { chatId, title } });
  }, []);

  const toggleSidebar = useCallback(() => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  }, []);

  const setSidebar = useCallback((open) => {
    dispatch({ type: 'SET_SIDEBAR', payload: open });
  }, []);

  const setLoading = useCallback((v) => {
    dispatch({ type: 'SET_LOADING', payload: v });
  }, []);

  const updateSettings = useCallback((settings) => {
    dispatch({ type: 'SET_SETTINGS', payload: settings });
  }, []);

  return (
    <AppContext.Provider
      value={{
        state,
        currentChat,
        chatGroups,
        createNewChat,
        selectChat,
        deleteChat,
        renameChat,
        addMessage,
        updateMessageContent,
        updateChatTitle,
        toggleSidebar,
        setSidebar,
        setLoading,
        updateSettings,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}

function applyTheme(theme) {
  if (typeof document === 'undefined') return;
  const prefersDark =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark = theme === 'dark' || (theme === 'system' && prefersDark);
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
}
