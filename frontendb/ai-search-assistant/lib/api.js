// ─── API Service Layer ────────────────────────────────────────────
// This layer is designed to be easily replaced with real backend calls.
// All functions currently return mock data with simulated delays.

export const MOCK_SOURCES = [
  {
    id: 'src-1',
    title: 'Nutrition and Weight Management Guide',
    domain: 'healthline.com',
    name: 'Healthline',
    description: 'Evidence-based nutrition information covering calorie-dense foods, macronutrient ratios, and meal planning strategies for healthy weight gain.',
    url: 'https://healthline.com',
  },
  {
    id: 'src-2',
    title: 'Sports Nutrition Research Review',
    domain: 'ncbi.nlm.nih.gov',
    name: 'PubMed / NCBI',
    description: 'Peer-reviewed research on protein synthesis, caloric surplus requirements, and the role of nutrient timing in muscle hypertrophy.',
    url: 'https://ncbi.nlm.nih.gov',
  },
  {
    id: 'src-3',
    title: 'Top Laptop Reviews 2024',
    domain: 'rtings.com',
    name: 'RTINGS',
    description: 'Comprehensive benchmark-driven laptop reviews covering performance, display quality, battery life, and value for different use cases.',
    url: 'https://rtings.com',
  },
  {
    id: 'src-4',
    title: 'React Documentation',
    domain: 'react.dev',
    name: 'React Docs',
    description: 'Official React documentation covering hooks, state management, performance optimization, and advanced component patterns.',
    url: 'https://react.dev',
  },
  {
    id: 'src-5',
    title: 'Python Best Practices Guide',
    domain: 'realpython.com',
    name: 'Real Python',
    description: 'In-depth Python tutorials covering async programming, data structures, testing patterns, and production-ready code organization.',
    url: 'https://realpython.com',
  },
];

export const MOCK_CONVERSATIONS = [
  {
    id: 'chat-1',
    title: 'Best foods for weight gain',
    createdAt: new Date().toISOString(),
    messages: [
      {
        id: 'msg-1',
        role: 'user',
        content: 'What are the best foods for gaining weight in a healthy way?',
        timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
      },
      {
        id: 'msg-2',
        role: 'assistant',
        content: `Here are some of the best calorie-dense foods that support healthy weight gain:

**High-Protein Foods**
- **Eggs** — Versatile, nutrient-rich, and packed with healthy fats and protein. Great for breakfast or post-workout meals.
- **Chicken thighs** — Higher in fat than breasts, making them more calorie-dense while still delivering ~25g protein per 100g.
- **Greek yogurt** — Dense in protein and probiotics. Full-fat varieties add substantial calories.
- **Salmon** — Rich in omega-3 fatty acids and high-quality protein, supporting both muscle growth and overall health.

**Calorie-Dense Whole Foods**
- **Avocados** — Around 240 calories each, loaded with healthy monounsaturated fats.
- **Nuts and nut butters** — Almonds, walnuts, and peanut butter provide 150–200 calories per small serving.
- **Whole grains** — Oats, brown rice, and quinoa offer complex carbs for sustained energy.
- **Olive oil** — Adding a tablespoon to meals adds 120 calories with minimal volume.

**Practical Tips**
1. Aim for a **caloric surplus of 300–500 calories/day** above your maintenance level.
2. Prioritize **protein at every meal** (aim for 1.6–2.2g per kg of body weight).
3. Eat **every 3–4 hours** to keep calorie intake consistent throughout the day.
4. Consider **liquid calories** (smoothies, whole milk) if solid food volume feels overwhelming.

Consistent resistance training alongside increased food intake will help ensure the weight you gain is primarily lean muscle mass rather than fat.`,
        timestamp: new Date(Date.now() - 4 * 60000).toISOString(),
        sources: [MOCK_SOURCES[0], MOCK_SOURCES[1]],
        searchProgress: {
          steps: [
            { label: 'Searching nutrition databases', done: true },
            { label: 'Reading dietary research', done: true },
            { label: 'Cross-referencing studies', done: true },
            { label: 'Generating answer', done: true },
          ],
        },
      },
    ],
  },
  {
    id: 'chat-2',
    title: 'Best laptops for developers',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    messages: [
      {
        id: 'msg-3',
        role: 'user',
        content: 'What are the best laptops for software developers in 2024?',
        timestamp: new Date(Date.now() - 86400000 - 10 * 60000).toISOString(),
      },
      {
        id: 'msg-4',
        role: 'assistant',
        content: `The best developer laptops in 2024 depend on your workflow, but here are top picks across different priorities:

**Apple MacBook Pro 14" M3 Pro** — *Best overall for most developers*
The M3 Pro chip offers exceptional single-core performance (crucial for compile times), excellent battery life (~18 hours), and a superb display. macOS's Unix foundation makes it ideal for web/backend development. Starting at $1,999.

**Framework Laptop 16** — *Best for Linux users and upgradeability*
A modular laptop that lets you swap components over time. Excellent Linux compatibility, strong performance, and an ethical supply chain. Ideal for developers who want full hardware control.

**Lenovo ThinkPad X1 Carbon Gen 12** — *Best for Windows enterprise devs*
Legendary keyboard quality, excellent build, and strong Windows 11 Pro support. Great for .NET/Azure-focused development. Business-grade security features.

**ASUS ROG Zephyrus G14** — *Best for GPU-intensive work*
If you're doing ML/AI development, 3D work, or gaming on the side, this AMD Ryzen + NVIDIA RTX combination delivers serious compute power in a relatively portable package.

**Key specs to prioritize:**
- **RAM:** 16GB minimum, 32GB recommended for running VMs or Docker heavily
- **Storage:** NVMe SSD, 512GB+ (1TB preferred)
- **Display:** 1080p minimum, though 2K/Retina is noticeably better for long sessions
- **Battery:** 10+ hours of realistic workday usage`,
        timestamp: new Date(Date.now() - 86400000 - 8 * 60000).toISOString(),
        sources: [MOCK_SOURCES[2]],
        searchProgress: {
          steps: [
            { label: 'Searching tech review sites', done: true },
            { label: 'Comparing benchmark results', done: true },
            { label: 'Analyzing user feedback', done: true },
            { label: 'Generating answer', done: true },
          ],
        },
      },
    ],
  },
  {
    id: 'chat-3',
    title: 'React project architecture',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    messages: [
      {
        id: 'msg-5',
        role: 'user',
        content: 'How should I structure a large React project?',
        timestamp: new Date(Date.now() - 86400000 - 20 * 60000).toISOString(),
      },
      {
        id: 'msg-6',
        role: 'assistant',
        content: `Structuring a large React project well makes the difference between a codebase that scales gracefully and one that becomes a maintenance burden. Here's an approach that works well in production:

**Recommended folder structure:**
\`\`\`
src/
├── components/        # Reusable UI components
│   ├── ui/           # Primitives (Button, Input, Modal)
│   └── features/     # Feature-specific components
├── pages/ or app/    # Route-level components
├── hooks/            # Custom React hooks
├── contexts/         # React Context providers
├── services/         # API calls and data fetching
├── utils/            # Pure utility functions
├── types/            # TypeScript types/interfaces
└── constants/        # App-wide constants
\`\`\`

**Key principles:**

1. **Co-locate related files** — Keep a component's CSS, tests, and hooks close to the component itself. This makes deleting or moving features easier.

2. **Feature-based organization at scale** — Once you have more than ~15 routes, group by feature rather than type:
   \`\`\`
   features/
   ├── auth/
   │   ├── components/
   │   ├── hooks/
   │   └── api.js
   ├── dashboard/
   └── settings/
   \`\`\`

3. **Centralize state thoughtfully** — Use local state for UI concerns, Context for cross-cutting data (auth, theme), and a library like Zustand for complex shared state. Avoid over-centralizing.

4. **Typed API layer** — Keep all API calls in a dedicated service layer. This makes mocking in tests trivial and backend changes isolated to one place.

5. **Barrel exports** — Use \`index.js\` files to create clean import paths:
   \`\`\`js
   import { Button, Input } from '@/components/ui';
   \`\`\`

The most important rule: **consistency beats perfection**. Pick a convention and apply it uniformly across the entire codebase.`,
        timestamp: new Date(Date.now() - 86400000 - 18 * 60000).toISOString(),
        sources: [MOCK_SOURCES[3]],
      },
    ],
  },
  {
    id: 'chat-4',
    title: 'Python async programming',
    createdAt: new Date(Date.now() - 3 * 86400000).toISOString(),
    messages: [
      {
        id: 'msg-7',
        role: 'user',
        content: 'Can you explain async/await in Python with practical examples?',
        timestamp: new Date(Date.now() - 3 * 86400000).toISOString(),
      },
      {
        id: 'msg-8',
        role: 'assistant',
        content: `Python's \`async/await\` syntax enables writing concurrent code that's readable and maintainable. Here's what you need to know:

**The core concept**

Async code uses cooperative multitasking — functions voluntarily yield control while waiting for I/O (network, disk, database). This means a single thread can handle thousands of concurrent operations.

\`\`\`python
import asyncio

async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(1)  # Simulates a database call
    return {"id": user_id, "name": "Alice"}

async def main():
    user = await fetch_user(42)
    print(user)

asyncio.run(main())
\`\`\`

**Concurrent execution with gather()**

The real power comes from running multiple coroutines simultaneously:

\`\`\`python
async def fetch_all_users(ids: list[int]) -> list[dict]:
    tasks = [fetch_user(uid) for uid in ids]
    # Runs all fetches concurrently, not sequentially
    results = await asyncio.gather(*tasks)
    return results

# Fetches 100 users in ~1s instead of ~100s
users = asyncio.run(fetch_all_users(range(100)))
\`\`\`

**Practical HTTP requests with httpx**

\`\`\`python
import httpx

async def get_posts() -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/posts")
        return response.json()
\`\`\`

**When to use async vs threads**
- Use **async** for I/O-bound tasks (APIs, databases, file operations)
- Use **threads/multiprocessing** for CPU-bound tasks (image processing, ML inference)

Mixing the two is possible but requires care — use \`asyncio.run_in_executor()\` to run blocking code without freezing your event loop.`,
        timestamp: new Date(Date.now() - 3 * 86400000 + 60000).toISOString(),
        sources: [MOCK_SOURCES[4]],
      },
    ],
  },
  {
    id: 'chat-5',
    title: 'TypeScript vs JavaScript',
    createdAt: new Date(Date.now() - 10 * 86400000).toISOString(),
    messages: [
      {
        id: 'msg-9',
        role: 'user',
        content: 'Should I use TypeScript or JavaScript for my next project?',
        timestamp: new Date(Date.now() - 10 * 86400000).toISOString(),
      },
      {
        id: 'msg-10',
        role: 'assistant',
        content: `**Short answer:** Use TypeScript for projects that will be maintained over time, involve multiple developers, or have complex data shapes. Stick with JavaScript for quick scripts, small prototypes, or when the team isn't familiar with TypeScript.

**Why TypeScript wins in production**

TypeScript's static typing catches entire categories of bugs at compile time rather than runtime. Refactoring becomes dramatically safer — rename a property and the compiler tells you everywhere it's used. IDE autocomplete becomes genuinely useful rather than guesswork.

**The real cost**

There is a genuine onboarding cost. TypeScript's type system is powerful but has a learning curve — generics, mapped types, and conditional types can be intimidating. This cost is worth paying for most teams working on code that lasts more than a few weeks.

**My recommendation**

- **New team project or app:** Use TypeScript from day one. Retrofitting later is painful.
- **Solo quick prototype:** JavaScript is fine. You can add types later if it matures.
- **Library you're publishing:** TypeScript with \`.d.ts\` exports — consumers will thank you.
- **Learning project:** Either works; TypeScript will teach you more about the language.

Modern Next.js, Vite, and React all have excellent TypeScript support with zero configuration required.`,
        timestamp: new Date(Date.now() - 10 * 86400000 + 120000).toISOString(),
        sources: [],
      },
    ],
  },
];

// ─── Mock AI Responses ─────────────────────────────────────────
export const MOCK_AI_RESPONSES = [
  {
    content: `That's a great question. Let me break this down for you with the most relevant information I can find.

**Key Points**

The answer depends on several factors that are worth considering carefully:

1. **Context matters** — The best approach varies significantly based on your specific situation, goals, and constraints.

2. **Evidence-based thinking** — Rather than relying on intuition alone, looking at research and real-world examples gives us a clearer picture.

3. **Practical considerations** — Implementation and long-term sustainability are just as important as the theoretical ideal.

**What the research suggests**

Most evidence points toward a balanced approach that combines multiple strategies rather than relying on any single method. This tends to produce better outcomes across a variety of scenarios.

**My recommendation**

Start with the fundamentals, measure your results, and iterate based on what you observe. Avoid over-optimizing before you have data to guide those optimizations.

Is there a specific aspect of this you'd like me to explore in more depth?`,
    sources: [MOCK_SOURCES[0], MOCK_SOURCES[2]],
    searchProgress: {
      steps: [
        { label: 'Searching relevant sources', done: true },
        { label: 'Reading key pages', done: true },
        { label: 'Synthesizing information', done: true },
        { label: 'Generating answer', done: true },
      ],
    },
  },
  {
    content: `Here's a comprehensive overview of what you're asking about:

**Overview**

This is a topic where the conventional wisdom doesn't always hold up to scrutiny. Let me walk you through what actually matters.

**The fundamentals**

\`\`\`
Key insight: Focus on the 20% of factors that drive 80% of results.
\`\`\`

Most people overcomplicate this. The fundamentals are:
- Consistency over intensity
- Systems over goals
- Progress over perfection

**A practical framework**

Think of it in three phases:

*Phase 1 — Foundation:* Establish the basics before optimizing anything. This is where most effort should go early on.

*Phase 2 — Iteration:* Once you have a working foundation, measure what's happening and make targeted improvements.

*Phase 3 — Optimization:* Only optimize when you have enough data to know what's actually worth improving.

**Common mistakes to avoid**

1. Starting with optimization before establishing fundamentals
2. Measuring the wrong metrics
3. Changing too many variables at once, making it impossible to know what's working

Let me know if you want me to go deeper on any of these areas.`,
    sources: [MOCK_SOURCES[1], MOCK_SOURCES[3]],
  },
  {
    content: `Great question — here's what you need to know:

The short version: **it depends**, but I can give you a clear framework for making the right decision for your situation.

**The core trade-offs**

| Approach | Best for | Watch out for |
|----------|----------|---------------|
| Option A | Speed and simplicity | Doesn't scale well |
| Option B | Long-term maintainability | Higher upfront cost |
| Option C | Flexibility | Requires more expertise |

**My recommendation**

Based on what you've described, I'd lean toward the second approach because it gives you the best balance of initial simplicity and future flexibility. You can always optimize later once you have real-world data about where the bottlenecks actually are.

**Next steps**

1. Start with a minimal implementation to validate the core concept
2. Gather feedback and metrics in the first few weeks
3. Refactor based on what you learn

This approach minimizes risk while keeping your options open as requirements evolve.

Want me to walk through any specific part of this in more detail?`,
    sources: [MOCK_SOURCES[4]],
  },
];

// ─── API Functions ─────────────────────────────────────────────
// These are structured to be easily replaced with real API calls.

export async function sendMessage(chatId, message) {
  // Simulate network delay
  await delay(800 + Math.random() * 400);

  const response = MOCK_AI_RESPONSES[Math.floor(Math.random() * MOCK_AI_RESPONSES.length)];

  return {
    id: generateId(),
    role: 'assistant',
    content: response.content,
    timestamp: new Date().toISOString(),
    sources: response.sources || [],
    searchProgress: response.searchProgress || null,
  };
}

export async function createChat() {
  await delay(100);
  return {
    id: generateId('chat'),
    title: 'New conversation',
    createdAt: new Date().toISOString(),
    messages: [],
  };
}

export async function deleteChat(chatId) {
  await delay(100);
  return { success: true };
}

export async function renameChat(chatId, newTitle) {
  await delay(100);
  return { success: true, title: newTitle };
}

export async function getChat(chatId) {
  await delay(200);
  return MOCK_CONVERSATIONS.find(c => c.id === chatId) || null;
}

export async function getChats() {
  await delay(200);
  return MOCK_CONVERSATIONS;
}

// ─── Helpers ───────────────────────────────────────────────────
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function generateId(prefix = 'id') {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function groupChatsByDate(chats) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);
  const sevenDaysAgo = new Date(today.getTime() - 7 * 86400000);

  const groups = {
    today: [],
    yesterday: [],
    previous7Days: [],
    older: [],
  };

  chats.forEach(chat => {
    const chatDate = new Date(chat.createdAt);
    if (chatDate >= today) {
      groups.today.push(chat);
    } else if (chatDate >= yesterday) {
      groups.yesterday.push(chat);
    } else if (chatDate >= sevenDaysAgo) {
      groups.previous7Days.push(chat);
    } else {
      groups.older.push(chat);
    }
  });

  return groups;
}
