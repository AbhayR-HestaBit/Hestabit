export default function UsersPage() {
  const users = [
    { id: 1, name: "Duis non ", email: "Duis@example.com", role: "Admin" },
    { id: 2, name: "Quis aute", email: "Quis@example.com", role: "Editor" },
    { id: 3, name: "Culpa laborum", email: "Culpa@example.com", role: "Viewer" },
  ];


  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-90">
        Users
      </h1>

      <div className="overflow-x-auto bg-white rounded shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-600">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Email</th>
              <th className="px-4 py-3 text-left">Role</th>
            </tr>
          </thead>

          <tbody>
            {users.map((user) => (
              <tr
                key={user.id}
                className="border-t hover:bg-gray-200"
              >
                <td className="px-4 py-3 text-gray-500">{user.name}</td>
                <td className="px-4 py-3 text-gray-500">{user.email}</td>
                <td className="px-4 py-3 text-gray-500">{user.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
