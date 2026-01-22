"use client";

import { useState } from "react";
import Link from "next/link";

export default function Sidebar() {
  const [layoutsOpen, setLayoutsOpen] = useState(false);
  const [pagesOpen, setPagesOpen] = useState(false);

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 h-full p-4 text-sm">
      
      {/* Core */}
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

      {/* Interface */}
      <div className="mb-4 mt-6 text-xs uppercase text-slate-400">
        Interface
      </div>

      <ul className="space-y-2">

        {/* Layouts Dropdown */}
        <li>
          <button
            onClick={() => setLayoutsOpen(!layoutsOpen)}
            className="w-full text-left px-2 py-1 rounded hover:bg-slate-800 flex justify-between items-center"
          >
            <span>Layouts</span>
            <span>{layoutsOpen ? "▾" : "▸"}</span>
          </button>

          {layoutsOpen && (
            <ul className="ml-4 mt-1 space-y-1 text-slate-400">
              <li>
                <Link
                  href="#"
                  className="block px-2 py-1 rounded hover:bg-slate-800"
                >
                  Static
                </Link>
              </li>
              <li>
                <Link
                  href="#"
                  className="block px-2 py-1 rounded hover:bg-slate-800"
                >
                  Light
                </Link>
              </li>
              <li>
                <Link
                  href="#"
                  className="block px-2 py-1 rounded hover:bg-slate-800"
                >
                  Dark
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* Pages Dropdown */}
        <li>
          <button
            onClick={() => setPagesOpen(!pagesOpen)}
            className="w-full text-left px-2 py-1 rounded hover:bg-slate-800 flex justify-between items-center"
          >
            <span>Pages</span>
            <span>{pagesOpen ? "▾" : "▸"}</span>
          </button>

          {pagesOpen && (
            <ul className="ml-4 mt-1 space-y-1 text-slate-400">
              <li>
                <Link
                  href="/about"
                  className="block px-2 py-1 rounded hover:bg-slate-800"
                >
                  About
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard/profile"
                  className="block px-2 py-1 rounded hover:bg-slate-800"
                >
                  Profile
                </Link>
              </li>
            </ul>
          )}
        </li>
      </ul>

      {/* Addons */}
      <div className="mb-4 mt-6 text-xs uppercase text-slate-400">
        Addons
      </div>

      <ul className="space-y-2">
        <li>
          <Link
            href="#"
            className="block px-2 py-1 rounded hover:bg-slate-800"
          >
            Charts
          </Link>
        </li>

        <li>
          <Link
            href="#"
            className="block px-2 py-1 rounded hover:bg-slate-800"
          >
            Tables
          </Link>
        </li>
      </ul>
    </aside>
  );
}
