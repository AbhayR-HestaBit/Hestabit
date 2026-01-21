export default function Card({ title, children, footer }) {
  return (
    <div className="bg-white rounded shadow-sm border p-4">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {title}
        </h3>
      )}

      <div className="text-sm text-gray-600">
        {children}
      </div>

      {footer && (
        <div className="mt-4">
          {footer}
        </div>
      )}
    </div>
  );
}
