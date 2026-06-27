import "./info.css";

export default function Products() {
  const products = [
    { id: 1, name: "Samsung Galaxy A54", category: "ელექტრონიკა", price: "899.00 ₾", stock: 45 },
    { id: 2, name: "iPhone 15", category: "ელექტრონიკა", price: "2899.00 ₾", stock: 20 },
    { id: 3, name: "Nike Air Max", category: "ტანსაცმელი", price: "399.00 ₾", stock: 55 },
    { id: 4, name: "ბორჯომი (12 ბოთლი)", category: "საკვები", price: "18.00 ₾", stock: 500 },
    { id: 5, name: "Bosch სარეცხი მანქანა", category: "საყოფაცხოვრებო", price: "1599.00 ₾", stock: 10 },
  ];

  return (
    <div className="info-page">
      <h1 className="info-title">პროდუქტები</h1>
      <p className="info-subtitle">მონაცემთა ბაზაში არსებული პროდუქტების სია</p>

      <div className="info-card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>სახელი</th>
                <th>კატეგორია</th>
                <th>ფასი</th>
                <th>მარაგი</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>{p.id}</td>
                  <td>{p.name}</td>
                  <td>{p.category}</td>
                  <td className="price-col">{p.price}</td>
                  <td>{p.stock}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}