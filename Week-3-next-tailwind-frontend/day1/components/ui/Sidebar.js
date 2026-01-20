export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-slate-200 h-full p-4 text-sm">
      <div className="mb-6 text-xs uppercase text-slate-400">
        Core
      </div>

      <ul className="space-y-2">
        <li className="px-2 py-1 rounded bg-slate-800">
          Dashboard
        </li>
        <li className="px-2 py-1 rounded hover:bg-slate-800 cursor-pointer">
          Layouts
        </li>
        <li className="px-2 py-1 rounded hover:bg-slate-800 cursor-pointer">
          Pages
        </li>
        <li className="px-2 py-1 rounded hover:bg-slate-800 cursor-pointer">
          Charts
        </li>
        <li className="px-2 py-1 rounded hover:bg-slate-800 cursor-pointer">
          Tables
        </li>
      </ul>
    </aside>
  );
}
