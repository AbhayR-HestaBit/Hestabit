"use client";

import { useState } from "react";
import Link from "next/link";

export default function Sidebar() {
  const [layoutsOpen, setLayoutsOpen] = useState(false);
  const [pagesOpen, setPagesOpen] = useState(false);

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 h-full p-4 text-sm">
      
      <div className="mb-4 text-xs uppercase text-slate-400">
        Core
      </div>

      <ul className="space-y-2">
        <li>
          <Link
            href="/dashboard"
            className="block px-2 py-1 rounded bg-slate-800 hover:bg-slate-700"
          >
            Dashboard
          </Link>
        </li>
      </ul>

      <div className="mb-4 mt-6 text-xs uppercase text-slate-400">
        Interface
      </div>

      <ul className="space-y-2">
        <li>
          <button
            onClick={() => setLayoutsOpen(!layoutsOpen)}
            className="w-full text-left px-2 py-1 rounded hover:bg-slate-800 flex justify-between"
          >
            Layouts <span>{layoutsOpen ? "▾" : "▸"}</span>
          </button>

          {layoutsOpen && (
            <ul className="ml-4 mt-1 space-y-1 text-slate-400">
              <li className="hover:text-white">Static</li>
              <li className="hover:text-white">Light</li>
              <li className="hover:text-white">Dark</li>
            </ul>
          )}
        </li>

        <li>
          <button
            onClick={() => setPagesOpen(!pagesOpen)}
            className="w-full text-left px-2 py-1 rounded hover:bg-slate-800 flex justify-between"
          >
            Pages <span>{pagesOpen ? "▾" : "▸"}</span>
          </button>

          {pagesOpen && (
            <ul className="ml-4 mt-1 space-y-1 text-slate-400">
              <li>
                <Link href="/about">About</Link>
              </li>
              <li>
                <Link href="/dashboard/profile">Profile</Link>
              </li>
            </ul>
          )}
        </li>
      </ul>

      <div className="mb-4 mt-6 text-xs uppercase text-slate-400">
        Addons
      </div>

      <ul className="space-y-2">
        <li className="hover:bg-slate-800 px-2 py-1 rounded">Charts</li>
        <li className="hover:bg-slate-800 px-2 py-1 rounded">Tables</li>
      </ul>
    </aside>
  );
}
