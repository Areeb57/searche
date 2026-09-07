"use client";

import { Settings, CircleHelp, X } from "lucide-react";

import NewChatButton from "./NewChatButton";
import ChatHistory from "./ChatHistory";

export default function Sidebar({
    chats,
    currentChatId,
    sidebarOpen,
    onClose,
    onNewChat,
    onSelectChat,
    onOpenSettings,
}) {
    return (
        <>
            <aside
                className={`sidebar ${sidebarOpen ? "sidebar-open" : ""
                    }`}
            >
                <div className="sidebar-header">
                    <div className="logo">
                        <div className="logo-icon">AI</div>

                        <span>AI Search</span>
                    </div>

                    <button
                        className="icon-button sidebar-close"
                        onClick={onClose}
                        aria-label="Close sidebar"
                    >
                        <X size={18} />
                    </button>
                </div>

                <NewChatButton onClick={onNewChat} />

                <ChatHistory
                    chats={chats}
                    currentChatId={currentChatId}
                    onSelectChat={onSelectChat}
                />

                <div className="sidebar-bottom">
                    <button
                        className="sidebar-button"
                        onClick={onOpenSettings}
                        type="button"
                    >
                        <Settings size={18} />
                        <span>Settings</span>
                    </button>

                    <button className="sidebar-button">
                        <CircleHelp size={18} />
                        <span>Help</span>
                    </button>

                    <button className="profile-button">
                        <div className="profile-avatar">
                            U
                        </div>

                        <div>
                            <div className="profile-name">
                                User
                            </div>

                            <div className="profile-email">
                                user@example.com
                            </div>
                        </div>
                    </button>
                </div>
            </aside>

            {sidebarOpen && (
                <div
                    className="sidebar-overlay"
                    onClick={onClose}
                />
            )}
        </>
    );
}