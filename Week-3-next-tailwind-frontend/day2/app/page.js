import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";

export default function Home() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">
        Dashboard
      </h1>

      {/* Cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Primary Card">
          <Badge color="blue">Active</Badge>
        </Card>

        <Card title="Success Card">
          <Badge color="green">Completed</Badge>
        </Card>

        <Card title="Warning Card">
          <Badge color="red">Pending</Badge>
        </Card>

        <Card
          title="Action Card"
          footer={<Button>View Details</Button>}
        >
          Click below to see details
        </Card>
      </div>
    </div>
  );
}
