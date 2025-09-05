import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "../components/Header";
import Providers from "./Providers";
import Navbar from "../components/Navbar";
import PageContainer from "../components/PageContainer";
import SearchBox from "../components/SearchBox";



const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EventEase",
  description: "University Project",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning data-theme="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased
         bg-orange-200 dark:bg-gray-900 dark:text-white transition-colors duration-300`}
      >
        <Providers>
            <Header />
            <Navbar />
            <SearchBox />
            <PageContainer>
              {children}
              </PageContainer>
        </Providers>
      </body>
    </html>
  );
}
