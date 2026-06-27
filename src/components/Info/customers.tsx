export default function Customers() {
  const customers = [
    { id: 1, name: "Giorgi", email: "giorgi@mail.com", city: "Tbilisi" },
    { id: 2, name: "Nino", email: "nino@mail.com", city: "Batumi" },
    { id: 3, name: "Luka", email: "luka@mail.com", city: "Kutaisi" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">მომხმარებლები</h1>

      <div className="space-y-3">
        {customers.map((c) => (
          <div key={c.id} className="p-3 bg-gray-900 rounded">
            <p className="font-semibold">{c.name}</p>
            <p className="text-gray-400">{c.email}</p>
            <p className="text-gray-500 text-sm">{c.city}</p>
          </div>
        ))}
      </div>
    </div>
  );
}