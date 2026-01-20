import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import Navbar from "../components/ui/Navbar";
import Sidebar from "../components/ui/Sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Dashboard",
  description: "Admin Dashboard UI",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <div className="flex flex-col h-screen">
          {/* Top Navbar */}
          <Navbar />

          {/* Sidebar + Main */}
          <div className="flex flex-1 overflow-hidden">
            <Sidebar />

            <main className="flex-1 bg-slate-100 p-6 overflow-y-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
