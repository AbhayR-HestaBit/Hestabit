import Link from "next/link";

export default function StatCard({
  title,
  color = "blue",
  linkText = "View Details",
}) {
  const colors = {
    blue: "bg-blue-600",
    yellow: "bg-yellow-500",
    green: "bg-green-600",
    red: "bg-red-600",
  };

  return (
    <div
      className={`${colors[color]} text-white rounded shadow-sm`}
    >
      <div className="p-4">
        <h3 className="text-sm font-semibold">
          {title}
        </h3>
      </div>

      <div className="bg-black/10 px-4 py-2 text-sm flex justify-between items-center">
        <Link href="#" className="hover:underline">
          {linkText}
        </Link>
        <span>→</span>
      </div>
    </div>
  );
}
