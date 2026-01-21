export default function Input({ label, ...props }) {
  return (
    <div className="space-y-1">
      {label && (
        <label className="text-sm text-gray-600">
          {label}
        </label>
      )}
      <input
        className="w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        {...props}
      />
    </div>
  );
}
