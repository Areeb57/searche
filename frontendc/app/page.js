"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar/Sidebar";
import Header from "@/components/Header/Header";
import ChatWindow from "@/components/Chat/ChatWindow";
import SettingsModal from "@/components/Settings/SettingsModal";

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
  const [chats, setChats] = useState(initialChats);

  const [isHydrated, setIsHydrated] =
    useState(false);


  const [currentChatId, setCurrentChatId] =
    useState("chat-1");

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [input, setInput] = useState("");

  const [isLoading, setIsLoading] =
    useState(false);

  const [settingsOpen, setSettingsOpen] =
    useState(false);

  const [theme, setTheme] =
    useState("system");

  const [enterToSend, setEnterToSend] =
    useState(true);

  const [streaming, setStreaming] =
    useState(true);

  const currentChat = chats.find(
    (chat) => chat.id === currentChatId
  );


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
  }, [chats, currentChatId, isHydrated]);

  useEffect(() => {
    try {
      const savedChats =
        localStorage.getItem("ai-search-chats");

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

  useEffect(() => {
    const interval = setInterval(() => {
      setChats((previousChats) =>
        previousChats.map((chat) => ({
          ...chat,
          group: getChatGroup(chat.createdAt),
        }))
      );
    }, 60 * 1000);

    return () => clearInterval(interval);
  }, []);

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

      if (savedTheme) {
        setTheme(savedTheme);
      }

      if (savedEnterToSend !== null) {
        setEnterToSend(
          savedEnterToSend === "true"
        );
      }

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

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const root =
      document.documentElement;

    if (theme === "system") {
      root.removeAttribute("data-theme");
    } else {
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

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    localStorage.setItem(
      "ai-search-enter-to-send",
      String(enterToSend)
    );
  }, [enterToSend]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    localStorage.setItem(
      "ai-search-streaming",
      String(streaming)
    );
  }, [streaming]);


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

  function selectChat(chatId) {
    setCurrentChatId(chatId);

    if (
      typeof window !== "undefined" &&
      window.innerWidth <= 768
    ) {
      setSidebarOpen(false);
    }
  }

  function updateMessages(chatId, newMessages) {
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

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: userText,
    };

    const aiMessageId = crypto.randomUUID();

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
      // Step 1: Searching
      await wait(900);

      // Step 2: Reading
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

      // Step 3: Comparing
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

      // Step 4: Generating answer
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

      const result = await sendMessage(userText);

      // Research completed
      updateMessages(
        currentChatId,
        (messages) =>
          messages.map((message) =>
            message.id === aiMessageId
              ? {
                ...message,
                searching: false,
                searchStep: 5,
                sources: result.sources || [],
              }
              : message
          )
      );

      // Stream answer
      let streamedText = "";

      for (const character of result.response) {
        streamedText += character;

        updateMessages(
          currentChatId,
          (messages) =>
            messages.map((message) =>
              message.id === aiMessageId
                ? {
                  ...message,
                  content: streamedText,
                }
                : message
            )
        );

        await wait(12);
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

  function handleRegenerate() {
    console.log(
      "Regenerate is not implemented yet."
    );
  }

  async function wait(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
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
          messages={currentChat?.messages || []}
          isLoading={isLoading}
          onRegenerate={handleRegenerate}
        />

        <div className="input-container">
          <div className="message-input">
            <button
              className="input-icon"
              aria-label="Attach file"
              type="button"
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
                  !event.shiftKey &&
                  enterToSend
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
              type="button"
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
              type="button"
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