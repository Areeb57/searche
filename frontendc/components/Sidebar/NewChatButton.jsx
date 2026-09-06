"use client";

import { Plus } from "lucide-react";

export default function NewChatButton({ onClick }) {
    return (
        <button
            className="new-chat-button"
            onClick={onClick}
            aria-label="Start a new chat"
        >
            <Plus size={18} />
            <span>New Chat</span>
        </button>
    );
}