export default function Navbar({ onMenuClick }) {
  return (
    <header className="h-16 md:h-20 w-full bg-slate-900 text-white flex items-center px-4">
      <button
        onClick={onMenuClick}
        className="md:hidden mr-3 text-xl"
        aria-label="Open menu"
      >
        +
      </button>

      <span className="font-semibold text-sm md:text-base">
        Dashboard
      </span>

      <div className="ml-auto flex items-center gap-4">
        <input
          type="text"
          placeholder="Search..."
          className="hidden md:block px-3 py-1 text-sm rounded bg-slate-800 text-white focus:outline-none"
        />
        <span className="text-xs opacity-80">User</span>
      </div>
    </header>
  );
}
