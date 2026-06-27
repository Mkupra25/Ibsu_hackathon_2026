export default function Products() {
  const data = [
    { name: "Shoes", value: 120 },
    { name: "T-Shirts", value: 90 },
    { name: "Hoodies", value: 60 },
    { name: "Caps", value: 40 },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">პროდუქტები</h1>

      <div className="bg-gray-900 p-4 rounded">
        <p className="text-gray-400 mb-4">
          პროდუქტის გაყიდვები (გრაფიკი)
        </p>

        <div>
          <pre className="text-sm text-white">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}