import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Chipsana - AI Hardware Performance Calculator",
  description: "Calculate TCO, compare GPUs, and analyze AI infrastructure costs. Make informed decisions about AI hardware investments.",
  keywords: ["AI hardware", "GPU comparison", "TCO calculator", "cost per token", "H100", "A100", "ML infrastructure"],
  authors: [{ name: "Chipsana" }],
  openGraph: {
    title: "Chipsana - AI Hardware Performance Calculator",
    description: "Calculate TCO, compare GPUs, and analyze AI infrastructure costs",
    url: "https://chipsana.in",
    siteName: "Chipsana",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Chipsana - AI Hardware Performance Calculator",
    description: "Calculate TCO, compare GPUs, and analyze AI infrastructure costs",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
