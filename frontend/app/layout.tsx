import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Falcon 3 Chat",
  description: "Chat with Falcon3-1B-Instruct by TII",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full">{children}</body>
    </html>
  );
}
