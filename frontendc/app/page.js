"use client";

import { useEffect, useRef, useState } from "react";

import Sidebar from "@/components/Sidebar/Sidebar";
import Header from "@/components/Header/Header";
import ChatWindow from "@/components/Chat/ChatWindow";
import SettingsModal from "@/components/Settings/SettingsModal";
import MessageInput from "@/components/Input/MessageInput";

import { sendMessage } from "@/lib/api";

function getChatGroup(timestamp) {
  const now = new Date();
  const chatDate = new Date(timestamp);

  const startOfToday = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate()
  );

  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(
    startOfYesterday.getDate() - 1
  );

  const sevenDaysAgo = new Date(startOfToday);
  sevenDaysAgo.setDate(
    sevenDaysAgo.getDate() - 7
  );

  if (chatDate >= startOfToday) {
    return "Today";
  }

  if (chatDate >= startOfYesterday) {
    return "Yesterday";
  }

  if (chatDate >= sevenDaysAgo) {
    return "Previous 7 Days";
  }

  return "Older";
}

const initialChats = [
  {
    id: "chat-1",
    title: "AI Search Assistant",
    createdAt: 1000000000000,
    group: "Today",
    messages: [],
  },

  {
    id: "chat-2",
    title: "React project help",
    createdAt: 999999999000,
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
    createdAt: 999999998000,
    group: "Today",
    messages: [],
  },

  {
    id: "chat-4",
    title: "Python project",
    createdAt: 999999997000,
    group: "Yesterday",
    messages: [],
  },

  {
    id: "chat-5",
    title: "Web development",
    createdAt: 999999996000,
    group: "Yesterday",
    messages: [],
  },
];

export default function Home() {
  // --------------------------------
  // Chat state
  // --------------------------------

  const [chats, setChats] = useState(initialChats);

  const [isHydrated, setIsHydrated] =
    useState(false);

  const [currentChatId, setCurrentChatId] =
    useState("chat-1");

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");

  const [isLoading, setIsLoading] =
    useState(false);

  const stopRef = useRef(false);
  // --------------------------------
  // Settings state
  // --------------------------------

  const [settingsOpen, setSettingsOpen] =
    useState(false);

  const [theme, setTheme] =
    useState("system");

  const [enterToSend, setEnterToSend] =
    useState(true);

  const [streaming, setStreaming] =
    useState(true);

  // --------------------------------
  // Current chat
  // --------------------------------

  const currentChat = chats.find(
    (chat) => chat.id === currentChatId
  );

  // --------------------------------
  // Make sure current chat exists
  // --------------------------------

  useEffect(() => {
    if (!isHydrated || chats.length === 0) {
      return;
    }

    const chatExists = chats.some(
      (chat) => chat.id === currentChatId
    );

    if (!chatExists) {
      setCurrentChatId(chats[0].id);
    }
  }, [
    chats,
    currentChatId,
    isHydrated,
  ]);

  // --------------------------------
  // Load saved chats
  // --------------------------------

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    try {
      const savedChats =
        localStorage.getItem(
          "ai-search-chats"
        );

      if (savedChats) {
        setChats(JSON.parse(savedChats));
      }
    } catch (error) {
      console.error(
        "Could not load saved chats:",
        error
      );
    } finally {
      setIsHydrated(true);
    }
  }, []);

  // --------------------------------
  // Save chats
  // --------------------------------

  useEffect(() => {
    if (!isHydrated) {
      return;
    }

    try {
      localStorage.setItem(
        "ai-search-chats",
        JSON.stringify(chats)
      );
    } catch (error) {
      console.error(
        "Could not save chats:",
        error
      );
    }
  }, [chats, isHydrated]);

  // --------------------------------
  // Update chat groups every minute
  // --------------------------------

  useEffect(() => {
    const interval = setInterval(() => {
      setChats((previousChats) =>
        previousChats.map((chat) => ({
          ...chat,
          group: getChatGroup(
            chat.createdAt
          ),
        }))
      );
    }, 60 * 1000);

    return () =>
      clearInterval(interval);
  }, []);

  // --------------------------------
  // Load saved settings
  // --------------------------------

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    try {
      const savedTheme =
        localStorage.getItem(
          "ai-search-theme"
        );

      const savedEnterToSend =
        localStorage.getItem(
          "ai-search-enter-to-send"
        );

      const savedStreaming =
        localStorage.getItem(
          "ai-search-streaming"
        );

      // Theme
      if (
        savedTheme === "light" ||
        savedTheme === "dark" ||
        savedTheme === "system"
      ) {
        setTheme(savedTheme);
      }

      // Enter to send
      if (savedEnterToSend !== null) {
        setEnterToSend(
          savedEnterToSend === "true"
        );
      }

      // Streaming
      if (savedStreaming !== null) {
        setStreaming(
          savedStreaming === "true"
        );
      }
    } catch (error) {
      console.error(
        "Could not load settings:",
        error
      );
    }
  }, []);

  // --------------------------------
  // Apply theme
  // --------------------------------

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const root = document.documentElement;

    if (theme === "system") {
      // Remove manual theme so CSS can use
      // prefers-color-scheme
      root.removeAttribute("data-theme");
    } else {
      // Apply manually selected theme
      root.setAttribute(
        "data-theme",
        theme
      );
    }

    localStorage.setItem(
      "ai-search-theme",
      theme
    );
  }, [theme]);

  // --------------------------------
  // Save Enter-to-send setting
  // --------------------------------

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    localStorage.setItem(
      "ai-search-enter-to-send",
      String(enterToSend)
    );
  }, [enterToSend]);

  // --------------------------------
  // Save streaming setting
  // --------------------------------

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    localStorage.setItem(
      "ai-search-streaming",
      String(streaming)
    );
  }, [streaming]);

  // --------------------------------
  // Create handle suggenstion
  // --------------------------------

  function handleSuggestion(text) {
    setInput(text);
  }
  // --------------------------------
  // Create new chat
  // --------------------------------

  function createNewChat() {
    const newChat = {
      id: crypto.randomUUID(),
      title: "New conversation",
      createdAt: Date.now(),
      group: getChatGroup(Date.now()),
      messages: [],
    };

    setChats((previousChats) => [
      newChat,
      ...previousChats,
    ]);

    setCurrentChatId(newChat.id);
    setInput("");

    if (
      typeof window !== "undefined" &&
      window.innerWidth <= 768
    ) {
      setSidebarOpen(false);
    }
  }

  // --------------------------------
  // Select chat
  // --------------------------------

  function selectChat(chatId) {
    setCurrentChatId(chatId);

    if (
      typeof window !== "undefined" &&
      window.innerWidth <= 768
    ) {
      setSidebarOpen(false);
    }
  }

  // --------------------------------
  // Update messages
  // --------------------------------

  function updateMessages(
    chatId,
    newMessages
  ) {
    setChats((previousChats) =>
      previousChats.map((chat) => {
        if (chat.id !== chatId) {
          return chat;
        }

        const messages =
          typeof newMessages === "function"
            ? newMessages(chat.messages)
            : newMessages;

        return {
          ...chat,
          messages,
        };
      })
    );
  }

  // --------------------------------
  // Stop response
  // --------------------------------
  function handleStop() {
    stopRef.current = true;
    setIsLoading(false);
  }


  // --------------------------------
  // Generate chat title
  // --------------------------------

  function generateChatTitle(text) {
    const cleanedText = text
      .replace(/\s+/g, " ")
      .trim();

    if (!cleanedText) {
      return "New conversation";
    }

    if (cleanedText.length <= 40) {
      return cleanedText;
    }

    return `${cleanedText.slice(0, 40)}...`;
  }

  // --------------------------------
  // Send message
  // --------------------------------

  async function handleSendMessage() {
    if (!input.trim() || isLoading) {
      return;
    }

    const userText = input.trim();

    setInput("");
    setIsLoading(true);

    const chat = chats.find(
      (item) => item.id === currentChatId
    );

    if (!chat) {
      setIsLoading(false);
      return;
    }

    // User message
    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: userText,
    };

    // AI message
    const aiMessageId =
      crypto.randomUUID();

    const aiMessage = {
      id: aiMessageId,
      role: "assistant",
      content: "",
      searching: true,
      searchStep: 1,
      sources: [],
    };

    const updatedMessages = [
      ...chat.messages,
      userMessage,
      aiMessage,
    ];

    stopRef.current = false;
    // Add user + AI message
    setChats((previousChats) =>
      previousChats.map((item) => {
        if (item.id !== currentChatId) {
          return item;
        }

        return {
          ...item,

          title:
            item.messages.length === 0 ||
              item.title === "New conversation"
              ? generateChatTitle(userText)
              : item.title,

          messages: updatedMessages,
        };
      })
    );

    try {
      // --------------------------------
      // Step 1: Searching
      // --------------------------------

      await wait(900);

      // --------------------------------
      // Step 2: Reading
      // --------------------------------

      updateMessages(
        currentChatId,
        (messages) =>
          messages.map((message) =>
            message.id === aiMessageId
              ? {
                ...message,
                searchStep: 2,
              }
              : message
          )
      );

      await wait(900);

      // --------------------------------
      // Step 3: Comparing
      // --------------------------------

      updateMessages(
        currentChatId,
        (messages) =>
          messages.map((message) =>
            message.id === aiMessageId
              ? {
                ...message,
                searchStep: 3,
              }
              : message
          )
      );

      await wait(900);

      // --------------------------------
      // Step 4: Generating answer
      // --------------------------------

      updateMessages(
        currentChatId,
        (messages) =>
          messages.map((message) =>
            message.id === aiMessageId
              ? {
                ...message,
                searchStep: 4,
              }
              : message
          )
      );

      // Get mock response
      const result =
        await sendMessage(userText);

      // --------------------------------
      // Research completed
      // --------------------------------

      updateMessages(
        currentChatId,
        (messages) =>
          messages.map((message) =>
            message.id === aiMessageId
              ? {
                ...message,
                searching: false,
                searchStep: 5,
                sources:
                  result.sources || [],
              }
              : message
          )
      );

      // --------------------------------
      // Stream answer
      // --------------------------------

      if (streaming) {
        for (let i = 0; i < result.response.length; i++) {
          if (stopRef.current) {
            break;
          }

          await new Promise((resolve) =>
            setTimeout(resolve, 12)
          );

          if (stopRef.current) {
            break;
          }

          updateMessages(
            currentChatId,
            (messages) =>
              messages.map((message) =>
                message.id === aiMessageId
                  ? {
                    ...message,
                    content: result.response.slice(0, i + 1),
                  }
                  : message
              )
          );
        }
      } else {
        updateMessages(
          currentChatId,
          (messages) =>
            messages.map((message) =>
              message.id === aiMessageId
                ? {
                  ...message,
                  content: result.response,
                }
                : message
            )
        );
      }
    } catch (error) {
      console.error(
        "Failed to send message:",
        error
      );

      updateMessages(
        currentChatId,
        (messages) =>
          messages.map((message) =>
            message.id === aiMessageId
              ? {
                ...message,
                searching: false,
                searchStep: 5,
                content:
                  "Sorry, something went wrong while generating the response.",
              }
              : message
          )
      );
    } finally {
      setIsLoading(false);
    }
  }

  // --------------------------------
  // Regenerate response
  // --------------------------------

  function handleRegenerate() {
    console.log(
      "Regenerate is not implemented yet."
    );
  }

  // --------------------------------
  // Delay helper
  // --------------------------------

  async function wait(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
  }

  // --------------------------------
  // UI
  // --------------------------------

  return (
    <main className="app">
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        sidebarOpen={sidebarOpen}
        onClose={() =>
          setSidebarOpen(false)
        }
        onNewChat={createNewChat}
        onSelectChat={selectChat}
        onOpenSettings={() =>
          setSettingsOpen(true)
        }
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
          onSuggestion={handleSuggestion}
        />

        <MessageInput
          value={input}
          onChange={setInput}
          onSend={handleSendMessage}
          onStop={handleStop}
          isLoading={isLoading}
          enterToSend={enterToSend}
        />
      </section>

      <SettingsModal
        open={settingsOpen}
        onClose={() =>
          setSettingsOpen(false)
        }
        theme={theme}
        onThemeChange={setTheme}
        enterToSend={enterToSend}
        onEnterToSendChange={
          setEnterToSend
        }
        streaming={streaming}
        onStreamingChange={setStreaming}
      />
    </main>
  );
}