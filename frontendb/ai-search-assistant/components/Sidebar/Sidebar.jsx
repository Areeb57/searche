'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Plus, MessageSquare, Settings, HelpCircle, User,
  MoreHorizontal, Pencil, Trash2, X, Zap
} from 'lucide-react';
import { useApp } from '@/contexts/AppContext';
import styles from './Sidebar.module.css';

// ─── Sidebar ──────────────────────────────────────────────────
export default function Sidebar({ onOpenSettings }) {
  const {
    state, currentChat, chatGroups,
    createNewChat, selectChat, deleteChat, renameChat,
  } = useApp();

  return (
    <aside className={`${styles.sidebar} ${state.sidebarOpen ? styles.open : ''}`}>
      <div className={styles.inner}>
        {/* Brand */}
        <div className={styles.brand}>
          <div className={styles.logo}>
            <Zap size={18} strokeWidth={2.5} />
          </div>
          <span className={styles.brandName}>Meridian</span>
        </div>

        {/* New Chat */}
        <button className={styles.newChatBtn} onClick={createNewChat}>
          <Plus size={16} strokeWidth={2.5} />
          <span>New chat</span>
        </button>

        {/* History */}
        <div className={styles.history}>
          <ChatGroup
            label="Today"
            chats={chatGroups.today}
            currentId={state.currentChatId}
            onSelect={selectChat}
            onDelete={deleteChat}
            onRename={renameChat}
          />
          <ChatGroup
            label="Yesterday"
            chats={chatGroups.yesterday}
            currentId={state.currentChatId}
            onSelect={selectChat}
            onDelete={deleteChat}
            onRename={renameChat}
          />
          <ChatGroup
            label="Previous 7 days"
            chats={chatGroups.previous7Days}
            currentId={state.currentChatId}
            onSelect={selectChat}
            onDelete={deleteChat}
            onRename={renameChat}
          />
          <ChatGroup
            label="Older"
            chats={chatGroups.older}
            currentId={state.currentChatId}
            onSelect={selectChat}
            onDelete={deleteChat}
            onRename={renameChat}
          />
        </div>

        {/* Bottom nav */}
        <div className={styles.bottom}>
          <button className={styles.navItem} onClick={onOpenSettings}>
            <Settings size={16} />
            <span>Settings</span>
          </button>
          <button className={styles.navItem}>
            <HelpCircle size={16} />
            <span>Help</span>
          </button>
          <button className={styles.navItem}>
            <User size={16} />
            <span>Account</span>
          </button>
        </div>
      </div>
    </aside>
  );
}

// ─── Chat Group ───────────────────────────────────────────────
function ChatGroup({ label, chats, currentId, onSelect, onDelete, onRename }) {
  if (!chats.length) return null;
  return (
    <div className={styles.group}>
      <p className={styles.groupLabel}>{label}</p>
      {chats.map(chat => (
        <ChatItem
          key={chat.id}
          chat={chat}
          isActive={chat.id === currentId}
          onSelect={onSelect}
          onDelete={onDelete}
          onRename={onRename}
        />
      ))}
    </div>
  );
}

// ─── Chat Item ─────────────────────────────────────────────────
function ChatItem({ chat, isActive, onSelect, onDelete, onRename }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(chat.title);
  const menuRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (renaming && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [renaming]);

  function handleRenameSubmit() {
    const trimmed = renameValue.trim();
    if (trimmed && trimmed !== chat.title) {
      onRename(chat.id, trimmed);
    }
    setRenaming(false);
  }

  function handleRenameKeyDown(e) {
    if (e.key === 'Enter') handleRenameSubmit();
    if (e.key === 'Escape') {
      setRenameValue(chat.title);
      setRenaming(false);
    }
  }

  return (
    <div
      className={`${styles.chatItem} ${isActive ? styles.chatItemActive : ''}`}
      onClick={() => !renaming && onSelect(chat.id)}
    >
      <MessageSquare size={14} className={styles.chatIcon} />

      {renaming ? (
        <input
          ref={inputRef}
          className={styles.renameInput}
          value={renameValue}
          onChange={e => setRenameValue(e.target.value)}
          onBlur={handleRenameSubmit}
          onKeyDown={handleRenameKeyDown}
          onClick={e => e.stopPropagation()}
        />
      ) : (
        <span className={styles.chatTitle}>{chat.title}</span>
      )}

      {!renaming && (
        <div className={styles.chatMenu} ref={menuRef}>
          <button
            className={styles.menuTrigger}
            onClick={e => { e.stopPropagation(); setMenuOpen(v => !v); }}
            aria-label="Chat options"
          >
            <MoreHorizontal size={14} />
          </button>
          {menuOpen && (
            <div className={styles.menuDropdown}>
              <button
                className={styles.menuOption}
                onClick={e => {
                  e.stopPropagation();
                  setRenaming(true);
                  setMenuOpen(false);
                }}
              >
                <Pencil size={13} />
                <span>Rename</span>
              </button>
              <button
                className={`${styles.menuOption} ${styles.menuOptionDanger}`}
                onClick={e => {
                  e.stopPropagation();
                  onDelete(chat.id);
                  setMenuOpen(false);
                }}
              >
                <Trash2 size={13} />
                <span>Delete</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
