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
        sources: [
            {
                id: "weight-1",
                name: "Healthline",
                domain: "healthline.com",
                title: "Foods to Help You Gain Weight",
                description:
                    "An overview of nutritious foods and strategies that can help support healthy weight gain.",
                url: "https://www.healthline.com/nutrition/18-foods-to-gain-weight",
            },
            {
                id: "weight-2",
                name: "Medical News Today",
                domain: "medicalnewstoday.com",
                title: "Healthy ways to gain weight",
                description:
                    "Information about increasing calorie intake and choosing nutritious foods for weight gain.",
                url: "https://www.medicalnewstoday.com/articles/321982",
            },
            {
                id: "weight-3",
                name: "NHS",
                domain: "nhs.uk",
                title: "Healthy ways to gain weight",
                description:
                    "General guidance on gaining weight through a balanced diet and nutritious food choices.",
                url: "https://www.nhs.uk/live-well/healthy-weight/",
            },
        ],
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
        sources: [
            {
                id: "react-1",
                name: "React",
                domain: "react.dev",
                title: "React Documentation",
                description:
                    "Official React documentation covering components, state, hooks, and building user interfaces.",
                url: "https://react.dev/",
            },
            {
                id: "react-2",
                name: "Next.js",
                domain: "nextjs.org",
                title: "Next.js Documentation",
                description:
                    "Official Next.js documentation covering routing, rendering, components, and application development.",
                url: "https://nextjs.org/docs",
            },
            {
                id: "react-3",
                name: "MDN",
                domain: "developer.mozilla.org",
                title: "JavaScript Guide",
                description:
                    "Reference material for JavaScript concepts used when building modern web applications.",
                url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            },
        ],
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
        sources: [
            {
                id: "laptop-1",
                name: "PCMag",
                domain: "pcmag.com",
                title: "Laptop Buying Guide",
                description:
                    "A guide to important laptop specifications and factors to consider when choosing a computer.",
                url: "https://www.pcmag.com/picks/the-best-laptops",
            },
            {
                id: "laptop-2",
                name: "Microsoft",
                domain: "microsoft.com",
                title: "Windows PCs",
                description:
                    "Information about Windows PCs and the hardware available for different computing needs.",
                url: "https://www.microsoft.com/en-us/windows",
            },
        ],
    },
];

const defaultResponse = `I can help you research topics, compare information, summarize sources, and organize answers.

For this prototype, my responses are generated from mock frontend data.

Later, this function can be connected to your real backend without changing the chat interface.`;

const defaultSources = [
    {
        id: "default-1",
        name: "Wikipedia",
        domain: "wikipedia.org",
        title: "General reference information",
        description:
            "A general reference source that can provide background information on many topics.",
        url: "https://www.wikipedia.org/",
    },
    {
        id: "default-2",
        name: "MDN Web Docs",
        domain: "developer.mozilla.org",
        title: "Web development reference",
        description:
            "Technical documentation and reference material for web technologies.",
        url: "https://developer.mozilla.org/",
    },
];

export async function sendMessage(message) {
    await new Promise((resolve) =>
        setTimeout(resolve, 900)
    );

    const normalizedMessage = message.toLowerCase();

    const matchingResponse = mockResponses.find(
        (item) =>
            item.keywords.some((keyword) =>
                normalizedMessage.includes(keyword)
            )
    );

    if (matchingResponse) {
        return {
            response: matchingResponse.response,
            sources: matchingResponse.sources,
        };
    }

    return {
        response: defaultResponse,
        sources: defaultSources,
    };
}