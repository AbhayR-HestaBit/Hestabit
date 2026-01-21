import StatCard from "../components/ui/StatCard";
import PanelCard from "../components/ui/PanelCard";

export default function Home() {
  return (
    <div className="space-y-6">
      {/* Page Title */}
      <h1 className="text-2xl font-semibold text-gray-200">
        Dashboard
      </h1>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Primary Card" color="blue" />
        <StatCard title="Warning Card" color="yellow" />
        <StatCard title="Success Card" color="green" />
        <StatCard title="Danger Card" color="red" />
      </div>
      {/* Charts Section */}
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <PanelCard title="Area Chart Example">
    <div className="h-64 flex items-center justify-center text-gray-400">
      Chart will be added later
    </div>
  </PanelCard>

  <PanelCard title="Bar Chart Example">
    <div className="h-64 flex items-center justify-center text-gray-400">
      Chart will be added later
    </div>
  </PanelCard>
</div>

    </div>
  );
}
