export default function PanelCard({ title, children }) {
  return (
    <div className="bg-white border rounded shadow-sm">
      <div className="px-4 py-2 border-b text-sm font-semibold text-gray-800">
        {title}
      </div>
      <div className="p-4 text-sm text-gray-600">
        {children}
      </div>
    </div>
  );
}
