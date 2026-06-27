import "./info.css";

export default function Customers() {
  const customers = [
    { id: 1, name: "გიორგი ბერიძე", email: "g.beridze@gmail.com", city: "თბილისი" },
    { id: 2, name: "ნინო კვარაცხელია", email: "n.kvarackhelia@gmail.com", city: "თბილისი" },
    { id: 3, name: "დავით მამუკაძე", email: "d.mamukadze@gmail.com", city: "ბათუმი" },
    { id: 4, name: "მარიამ ჯავახიშვილი", email: "m.javakhishvili@gmail.com", city: "ქუთაისი" },
    { id: 5, name: "ალექსანდრე წერეთელი", email: "a.tsereteli@gmail.com", city: "თბილისი" },
  ];

  return (
    <div className="info-page">
      <h1 className="info-title">მომხმარებლები</h1>
      <p className="info-subtitle">რეგისტრირებული კლიენტების სია</p>

      <div className="info-card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>სრული სახელი</th>
                <th>ელ. ფოსტა</th>
                <th>ქალაქი</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.name}</td>
                  <td>{c.email}</td>
                  <td>{c.city}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}