"use client";

import {
    Menu,
    ChevronDown,
    Share2,
    MoreVertical,
} from "lucide-react";

export default function Header({
    title,
    onOpenSidebar,
}) {
    return (
        <header className="header">
            <div className="header-left">
                <button
                    className="icon-button mobile-menu"
                    onClick={onOpenSidebar}
                    aria-label="Open sidebar"
                >
                    <Menu size={20} />
                </button>

                <span className="conversation-title">
                    {title}
                </span>
            </div>

            <div className="header-right">
                <button className="model-selector">
                    <span>AI Search</span>
                    <ChevronDown size={15} />
                </button>

                <button
                    className="icon-button header-action"
                    aria-label="Share conversation"
                >
                    <Share2 size={17} />
                </button>

                <button
                    className="icon-button header-action"
                    aria-label="More options"
                >
                    <MoreVertical size={18} />
                </button>
            </div>
        </header>
    );
}