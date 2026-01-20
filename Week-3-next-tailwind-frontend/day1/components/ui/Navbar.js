export default function Navbar() {
  return (
    <header className="h-14 w-full bg-slate-800 text-white flex items-center px-4">
      <div className="font-semibold text-sm">
        Start Bootstrap
      </div>

      <div className="ml-auto flex items-center gap-4">
        <input
          placeholder="Search for..."
          className="hidden md:block px-3 py-1 text-sm rounded text-black"
        />
        <span className="text-xs opacity-80">User</span>
      </div>
    </header>
  );
}
