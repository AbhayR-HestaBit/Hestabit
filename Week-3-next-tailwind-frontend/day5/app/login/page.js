"use client";

import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="w-full max-w-md bg-zinc-300 p-6 rounded shadow space-y-5">

        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-800">
            Welcome back
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Please sign in to continue
          </p>
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">
            Email address
          </label>
          <input
            type="email"
            placeholder="you@example.com"
            className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring focus:ring-blue-200"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">
            Password
          </label>
          <input
            type="password"
            placeholder="••••••••"
            className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring focus:ring-blue-200"
          />
        </div>

        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              className="rounded border-gray-300"
            />
            Remember me
          </label>

          <Link
            href="#"
            className="text-blue-600 hover:underline"
          >
            Forgot password?
          </Link>
        </div>

        <button
          type="button"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Sign In
        </button>

        <p className="text-xs text-center text-gray-500">
          This is a UI-only login screen for demonstration purposes.
        </p>
      </div>
    </div>
  );
}
