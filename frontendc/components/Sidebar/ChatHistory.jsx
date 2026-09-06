"use client";

import ChatHistoryItem from "./ChatHistoryItem";

export default function ChatHistory({
    chats,
    currentChatId,
    onSelectChat,
}) {
    const groups = {
        Today: chats.filter((chat) => chat.group === "Today"),
        Yesterday: chats.filter(
            (chat) => chat.group === "Yesterday"
        ),
        "Previous 7 Days": chats.filter(
            (chat) => chat.group === "Previous 7 Days"
        ),
        Older: chats.filter(
            (chat) => chat.group === "Older"
        ),
    };

    return (
        <div className="chat-history">
            {Object.entries(groups).map(([groupName, groupChats]) => {
                if (groupChats.length === 0) {
                    return null;
                }

                return (
                    <div className="history-section" key={groupName}>
                        <div className="history-title">
                            {groupName}
                        </div>

                        {groupChats.map((chat) => (
                            <ChatHistoryItem
                                key={chat.id}
                                chat={chat}
                                active={chat.id === currentChatId}
                                onClick={() => onSelectChat(chat.id)}
                            />
                        ))}
                    </div>
                );
            })}
        </div>
    );
}