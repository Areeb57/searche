'use client';

import { useState, useRef, useEffect } from 'react';
import { Menu, ChevronDown, Share2, Settings, User, LogOut } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';
import styles from './Header.module.css';

const MODELS = [
  { id: 'meridian-pro', label: 'Meridian Pro', badge: 'Pro' },
  { id: 'meridian-fast', label: 'Meridian Fast', badge: null },
  { id: 'meridian-research', label: 'Meridian Research', badge: 'New' },
];

export default function Header({ onOpenSettings }) {
  const { state, currentChat, toggleSidebar } = useApp();
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [modelOpen, setModelOpen] = useState(false);
  const [userOpen, setUserOpen] = useState(false);
  const modelRef = useRef(null);
  const userRef = useRef(null);

  useEffect(() => {
    function handleClick(e) {
      if (modelRef.current && !modelRef.current.contains(e.target)) setModelOpen(false);
      if (userRef.current && !userRef.current.contains(e.target)) setUserOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <button
          className={styles.menuBtn}
          onClick={toggleSidebar}
          aria-label="Toggle sidebar"
        >
          <Menu size={18} />
        </button>
        <h1 className={styles.title}>
          {currentChat?.title || 'Meridian'}
        </h1>
      </div>

      <div className={styles.right}>
        {/* Model selector */}
        <div className={styles.dropdown} ref={modelRef}>
          <button
            className={styles.modelBtn}
            onClick={() => setModelOpen(v => !v)}
            aria-haspopup="listbox"
            aria-expanded={modelOpen}
          >
            <span className={styles.modelLabel}>{selectedModel.label}</span>
            {selectedModel.badge && (
              <span className={styles.modelBadge}>{selectedModel.badge}</span>
            )}
            <ChevronDown size={14} className={modelOpen ? styles.chevronOpen : ''} />
          </button>

          {modelOpen && (
            <div className={styles.dropdownMenu} role="listbox">
              {MODELS.map(model => (
                <button
                  key={model.id}
                  className={`${styles.dropdownItem} ${selectedModel.id === model.id ? styles.dropdownItemActive : ''}`}
                  role="option"
                  aria-selected={selectedModel.id === model.id}
                  onClick={() => { setSelectedModel(model); setModelOpen(false); }}
                >
                  <span>{model.label}</span>
                  {model.badge && <span className={styles.modelBadge}>{model.badge}</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Share (desktop only) */}
        <button className={`${styles.iconBtn} ${styles.desktopOnly}`} aria-label="Share conversation">
          <Share2 size={16} />
        </button>

        {/* User menu */}
        <div className={styles.dropdown} ref={userRef}>
          <button
            className={styles.avatarBtn}
            onClick={() => setUserOpen(v => !v)}
            aria-label="User menu"
          >
            <span>J</span>
          </button>

          {userOpen && (
            <div className={`${styles.dropdownMenu} ${styles.dropdownRight}`}>
              <div className={styles.userInfo}>
                <p className={styles.userName}>Jane Smith</p>
                <p className={styles.userEmail}>jane@example.com</p>
              </div>
              <div className={styles.dropdownDivider} />
              <button className={styles.dropdownItem} onClick={() => { onOpenSettings(); setUserOpen(false); }}>
                <Settings size={14} />
                <span>Settings</span>
              </button>
              <button className={styles.dropdownItem}>
                <LogOut size={14} />
                <span>Sign out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
