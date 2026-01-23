"use client";

import { useState } from "react";

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/ui/Navbar";
import Sidebar from "@/components/ui/Sidebar";


export default function RootLayout({ children }) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <html lang="en">
      <body className="bg-slate-100">
        <div className="flex flex-col h-screen">

           <Navbar onMenuClick={() => setMobileSidebarOpen(true)} />
          <div className="flex flex-1 overflow-hidden">

            <div className="hidden md:block">
              <Sidebar />
            </div>

            <main className="flex-1 p-4 md:p-6 overflow-y-auto">
              {children}
            </main>
          </div>

          {mobileSidebarOpen && (
            <div className="fixed inset-0 z-50 md:hidden">
              <div
                className="absolute inset-0 bg-black/40"
                onClick={() => setMobileSidebarOpen(false)}
              />

              <div className="relative w-64 h-full bg-slate-900">
                <Sidebar />
              </div>
            </div>
          )}
        </div>
      </body>
    </html>
  );
}
