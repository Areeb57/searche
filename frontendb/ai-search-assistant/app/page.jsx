'use client';

import { useState, useCallback, useRef } from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import Header from '@/components/Header/Header';
import ChatWindow from '@/components/Chat/ChatWindow';
import MessageInput from '@/components/Input/MessageInput';
import SettingsModal from '@/components/Settings/SettingsModal';
import { useApp } from '@/contexts/AppContext';
import { sendMessage, generateId } from '@/lib/api';

export default function HomePage() {
  const {
    state,
    addMessage,
    updateMessageContent,
    updateChatTitle,
    setLoading,
    createNewChat,
    setSidebar,
  } = useApp();

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [streamingMsgId, setStreamingMsgId] = useState(null);
  const abortRef = useRef(false);

  const handleSend = useCallback(async (text) => {
    if (state.isLoading) return;

    // Resolve (or create) the active chat
    let chatId = state.currentChatId;
    if (!chatId) {
      const newChat = createNewChat();
      chatId = newChat.id;
    }

    // Add user message
    addMessage(chatId, {
      id: generateId('msg'),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    });

    // Set title from first message
    const chat = state.chats.find(c => c.id === chatId);
    if (!chat || chat.title === 'New conversation' || chat.messages.length === 0) {
      updateChatTitle(chatId, text.length > 45 ? text.slice(0, 45) + '…' : text);
    }

    setLoading(true);
    abortRef.current = false;

    try {
      const response = await sendMessage(chatId, text);

      // Insert AI message (empty body — will be streamed in)
      const aiId = response.id;
      addMessage(chatId, {
        id: aiId,
        role: 'assistant',
        content: '',
        timestamp: response.timestamp,
        sources: response.sources || [],
        searchProgress: response.searchProgress || null,
      });

      setLoading(false);
      setStreamingMsgId(aiId);

      // Stream content in small chunks
      const full = response.content;
      const CHUNK = 12;
      const DELAY = 14; // ms per chunk → ~55 WPM feel

      for (let i = CHUNK; i < full.length; i += CHUNK) {
        if (abortRef.current) break;
        await sleep(DELAY);
        updateMessageContent(chatId, aiId, full.slice(0, i));
      }

      if (!abortRef.current) {
        updateMessageContent(chatId, aiId, full);
      }

      setStreamingMsgId(null);
    } catch (err) {
      console.error('Error sending message:', err);
      setLoading(false);
      setStreamingMsgId(null);
    }
  }, [
    state.isLoading,
    state.currentChatId,
    state.chats,
    addMessage,
    updateMessageContent,
    updateChatTitle,
    setLoading,
    createNewChat,
  ]);

  const handleSuggestion = useCallback((prompt) => handleSend(prompt), [handleSend]);
  const handleRegenerate = useCallback(() => { /* future: re-send last user msg */ }, []);

  return (
    <>
      <div className="app-layout">
        {/* Sidebar */}
        <Sidebar onOpenSettings={() => setSettingsOpen(true)} />

        {/* Mobile overlay */}
        {state.sidebarOpen && (
          <div
            className="app-overlay visible"
            onClick={() => setSidebar(false)}
            aria-hidden="true"
          />
        )}

        {/* Main content */}
        <main className="app-main">
          <Header onOpenSettings={() => setSettingsOpen(true)} />
          <ChatWindow
            onSuggestion={handleSuggestion}
            onRegenerate={handleRegenerate}
            streamingMessageId={streamingMsgId}
          />
          <MessageInput onSend={handleSend} />
        </main>
      </div>

      {settingsOpen && (
        <SettingsModal onClose={() => setSettingsOpen(false)} />
      )}
    </>
  );
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}
