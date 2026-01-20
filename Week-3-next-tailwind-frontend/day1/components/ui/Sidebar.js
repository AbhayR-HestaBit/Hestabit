export default function Sidebar() {
  return (
    <aside className="w-64 border-r h-screen p-4">
      <nav className="space-y-2 text-sm">
        <div className="font-medium">Menu</div>
        <div className="text-gray-600">Dashboard</div>
        <div className="text-gray-600">Users</div>
        <div className="text-gray-600">Settings</div>
      </nav>
    </aside>
  );
}
