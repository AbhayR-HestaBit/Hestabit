"use client";

export default function Modal({ open, title, children, onClose }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded w-full max-w-md p-4">
        <div className="flex justify-between items-center mb-2">
          <h2 className="font-semibold text-sm">
            {title}
          </h2>
          <button onClick={onClose}>✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}
