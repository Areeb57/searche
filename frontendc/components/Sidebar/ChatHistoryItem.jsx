"use client";

import { MoreHorizontal } from "lucide-react";

export default function ChatHistoryItem({
    chat,
    active,
    onClick,
}) {
    return (
        <div className={`chat-history-item ${active ? "active" : ""}`}>
            <button
                className="chat-history-title"
                onClick={onClick}
            >
                {chat.title}
            </button>

            <button
                className="chat-history-menu"
                aria-label={`Options for ${chat.title}`}
            >
                <MoreHorizontal size={16} />
            </button>
        </div>
    );
}