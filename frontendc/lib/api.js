const mockResponses = [
    {
        keywords: ["weight", "gain weight", "foods"],
        response: `Here are several calorie-dense foods that can help support healthy weight gain:

1. Rice and other whole grains
2. Eggs
3. Oats
4. Nuts and nut butter
5. Milk and yogurt
6. Avocados
7. Beans and legumes
8. Olive oil

For healthy weight gain, focus on adding nutritious calorie-dense foods to your regular meals rather than relying mainly on highly processed foods.

You can also combine protein, carbohydrates, and healthy fats in each meal.`,
    },

    {
        keywords: ["react", "next.js", "nextjs"],
        response: `React is a JavaScript library for building user interfaces, while Next.js is a framework built around React.

Next.js provides features such as:

1. File-based routing
2. Server and client components
3. Server-side rendering
4. Static generation
5. API and backend capabilities
6. Optimizations for production applications

For this project, we are using Next.js with React and keeping the application frontend-focused.`,
    },

    {
        keywords: ["laptop", "laptops", "computer"],
        response: `When comparing laptops, the most important specifications depend on your workload.

For general use, look at:

• CPU performance
• RAM
• SSD storage
• Display quality
• Battery life
• Weight and portability

For programming, I would generally prioritize a good CPU, at least 16 GB RAM, a fast SSD, and a comfortable keyboard.`,
    },
];

const defaultResponse = `I can help you research topics, compare information, summarize sources, and organize answers.

For this prototype, my responses are generated from mock frontend data.

Later, this function can be connected to your real backend without changing the chat interface.`;

const mockSources = [
    {
        id: "source-1",
        name: "Healthline",
        domain: "healthline.com",
        title: "Healthy Foods for Weight Gain",
        description:
            "A guide to nutritious, calorie-dense foods that can support healthy weight gain.",
        url: "https://www.healthline.com",
    },

    {
        id: "source-2",
        name: "Medical News Today",
        domain: "medicalnewstoday.com",
        title: "Foods That Can Help With Weight Gain",
        description:
            "Information about nutritious foods and eating strategies for increasing calorie intake.",
        url: "https://www.medicalnewstoday.com",
    },

    {
        id: "source-3",
        name: "WebMD",
        domain: "webmd.com",
        title: "Healthy Weight Gain Tips",
        description:
            "General information about nutritious eating and maintaining a balanced diet.",
        url: "https://www.webmd.com",
    },

    {
        id: "source-4",
        name: "Wikipedia",
        domain: "wikipedia.org",
        title: "Human Nutrition",
        description:
            "Background information about nutrition, food energy, and dietary components.",
        url: "https://www.wikipedia.org",
    },
];

export async function sendMessage(message) {
    const normalizedMessage = message.toLowerCase();

    const matchingResponse = mockResponses.find((item) =>
        item.keywords.some((keyword) =>
            normalizedMessage.includes(keyword)
        )
    );

    const response =
        matchingResponse?.response || defaultResponse;

    await new Promise((resolve) =>
        setTimeout(resolve, 900)
    );

    return {
        response,
        sources: mockSources,
    };
}