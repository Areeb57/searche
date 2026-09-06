"use client";

import { useState } from "react";

import Sidebar from "@/components/Sidebar/Sidebar";
import Header from "@/components/Header/Header";
import ChatWindow from "@/components/Chat/ChatWindow";

import { sendMessage } from "@/lib/api";

const initialChats = [
  {
    id: "chat-1",
    title: "AI Search Assistant",
    group: "Today",
    messages: [],
  },

  {
    id: "chat-2",
    title: "React project help",
    group: "Today",
    messages: [
      {
        id: "message-1",
        role: "user",
        content: "What is Next.js?",
      },
      {
        id: "message-2",
        role: "assistant",
        content:
          "Next.js is a React framework for building modern web applications.",
      },
    ],
  },

  {
    id: "chat-3",
    title: "Best laptops",
    group: "Today",
    messages: [],
  },

  {
    id: "chat-4",
    title: "Python project",
    group: "Yesterday",
    messages: [],
  },

  {
    id: "chat-5",
    title: "Web development",
    group: "Yesterday",
    messages: [],
  },
];

export default function Home() {
  const [chats, setChats] =
    useState(initialChats);

  const [currentChatId, setCurrentChatId] =
    useState("chat-1");

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [input, setInput] =
    useState("");

  const [isLoading, setIsLoading] =
    useState(false);

  const currentChat = chats.find(
    (chat) => chat.id === currentChatId
  );

  function createNewChat() {
    const newChat = {
      id: `chat-${Date.now()}`,
      title: "New Chat",
      group: "Today",
      messages: [],
    };

    setChats((previousChats) => [
      newChat,
      ...previousChats,
    ]);

    setCurrentChatId(newChat.id);

    setSidebarOpen(false);
  }

  function selectChat(chatId) {
    setCurrentChatId(chatId);
    setSidebarOpen(false);
  }

  function updateMessages(chatId, newMessages) {
    setChats((previousChats) =>
      previousChats.map((chat) =>
        chat.id === chatId
          ? {
            ...chat,
            messages: newMessages,
          }
          : chat
      )
    );
  }

  async function handleSendMessage() {
    const trimmedInput = input.trim();

    if (!trimmedInput || isLoading) {
      return;
    }

    const userMessage = {
      id: `message-${Date.now()}`,
      role: "user",
      content: trimmedInput,
    };

    const existingMessages =
      currentChat?.messages || [];

    const messagesWithUser = [
      ...existingMessages,
      userMessage,
    ];

    updateMessages(
      currentChatId,
      messagesWithUser
    );

    setInput("");
    setIsLoading(true);

    try {
      const response =
        await sendMessage(trimmedInput);

      const aiMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "",
        searching: true,
        searchStep: 1,
      };

      updateMessages(currentChatId, [
        ...messagesWithUser,
        aiMessage,
      ]);

      await streamResponse(
        currentChatId,
        messagesWithUser,
        aiMessage,
        response
      );
    } catch (error) {
      console.error(error);

      const errorMessage = {
        id: `message-${Date.now()}-error`,
        role: "assistant",
        content:
          "Something went wrong while generating the response.",
      };

      updateMessages(currentChatId, [
        ...messagesWithUser,
        errorMessage,
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  async function streamResponse(
    chatId,
    previousMessages,
    aiMessage,
    response
  ) {
    let currentText = "";

    for (const character of response) {
      currentText += character;

      const updatedMessage = {
        ...aiMessage,
        content: currentText,
      };

      updateMessages(chatId, [
        ...previousMessages,
        updatedMessage,
      ]);

      await new Promise((resolve) =>
        setTimeout(resolve, 12)
      );
    }
  }

  function handleRegenerate(messageId) {
    console.log(
      "Regenerate requested:",
      messageId
    );
  }

  function handleSuggestion(text) {
    setInput(text);
  }

  return (
    <main className="app">
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        sidebarOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={createNewChat}
        onSelectChat={selectChat}
      />

      <section className="main-area">
        <Header
          title={
            currentChat?.title ||
            "AI Search Assistant"
          }
          onOpenSidebar={() =>
            setSidebarOpen(true)
          }
        />

        <ChatWindow
          messages={
            currentChat?.messages || []
          }
          isLoading={isLoading}
          onRegenerate={handleRegenerate}
        />

        <div className="input-container">
          <div className="message-input">
            <button
              className="input-icon"
              aria-label="Attach file"
            >
              +
            </button>

            <textarea
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {
                  event.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Ask anything..."
              rows={1}
            />

            <button
              className="input-icon"
              aria-label="Voice input"
            >
              🎙
            </button>

            <button
              className="send-button"
              onClick={handleSendMessage}
              disabled={
                !input.trim() || isLoading
              }
              aria-label="Send message"
            >
              ↑
            </button>
          </div>

          <div className="input-disclaimer">
            AI Search Assistant can make mistakes.
            Check important information.
          </div>
        </div>
      </section>
    </main>
  );
}