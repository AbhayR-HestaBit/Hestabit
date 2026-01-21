import StatCard from "../components/ui/StatCard";

export default function Home() {
  return (
    <div className="space-y-6">
      {/* Page Title */}
      <h1 className="text-2xl font-semibold text-gray-900">
        Dashboard
      </h1>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Primary Card" color="blue" />
        <StatCard title="Warning Card" color="yellow" />
        <StatCard title="Success Card" color="green" />
        <StatCard title="Danger Card" color="red" />
      </div>
    </div>
  );
}
