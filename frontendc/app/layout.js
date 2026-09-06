import "./globals.css";

export const metadata = {
  title: "AI Search Assistant",
  description: "AI-powered search and research assistant",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}