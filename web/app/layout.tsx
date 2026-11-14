import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Way Out",
  description: "Every home called. Every rider matched. Nobody told help is coming until a driver says yes.",
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = { themeColor: "#0b0e13", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-dvh antialiased">{children}</body>
    </html>
  );
}
