export default function Orders() {
  const orders = [
    {
      id: 1,
      customer: "Giorgi",
      products: ["Shoes", "Cap"],
    },
    {
      id: 2,
      customer: "Nino",
      products: ["Hoodie"],
    },
    {
      id: 3,
      customer: "Luka",
      products: ["T-Shirt", "Shoes"],
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">შეკვეთები</h1>

      <div className="space-y-3">
        {orders.map((o) => (
          <div key={o.id} className="p-3 bg-gray-900 rounded">
            <p className="font-semibold">კლიენტი: {o.customer}</p>
            <p className="text-gray-400">
              პროდუქტები: {o.products.join(", ")}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}