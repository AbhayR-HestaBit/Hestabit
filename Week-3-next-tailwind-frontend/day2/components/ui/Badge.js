export default function Badge({ children, color = "gray" }) {
  const colors = {
    gray: "bg-gray-200 text-black-800",
    green: "bg-green-200 text-green-800",
    red: "bg-red-200 text-red-800",
    blue: "bg-blue-200 text-blue-800",
  };

  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs rounded ${colors[color]}`}
    >
      {children}
    </span>
  );
}
