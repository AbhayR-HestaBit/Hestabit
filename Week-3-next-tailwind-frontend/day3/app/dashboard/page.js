import StatCard from "@/components/ui/StatCard";
import PanelCard from "@/components/ui/PanelCard";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-100">
        Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Primary Card" color="blue" />
        <StatCard title="Warning Card" color="yellow" />
        <StatCard title="Success Card" color="green" />
        <StatCard title="Danger Card" color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PanelCard title="Area Chart Example">
          Chart placeholder
        </PanelCard>
        <PanelCard title="Bar Chart Example">
          Chart placeholder
        </PanelCard>
      </div>
    </div>
  );
}
