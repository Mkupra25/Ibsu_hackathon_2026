import "./info.css";

export default function Orders() {
  const orders = [
    { id: 101, customer: "გიორგი ბერიძე", date: "2026-06-25", amount: "899.00 ₾", status: "მიწოდებული" },
    { id: 102, customer: "ნინო კვარაცხელია", date: "2026-06-26", amount: "399.00 ₾", status: "გაგზავნილი" },
    { id: 103, customer: "დავით მამუკაძე", date: "2026-06-27", amount: "18.00 ₾", status: "მოლოდინში" },
    { id: 104, customer: "ალექსანდრე წერეთელი", date: "2026-06-27", amount: "1599.00 ₾", status: "მიწოდებული" },
  ];

  return (
    <div className="info-page">
      <h1 className="info-title">შეკვეთები</h1>
      <p className="info-subtitle">ბოლო შეკვეთების ისტორია</p>

      <div className="info-card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>შეკვეთის ID</th>
                <th>კლიენტი</th>
                <th>თარიღი</th>
                <th>თანხა</th>
                <th>სტატუსი</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>#{o.id}</td>
                  <td>{o.customer}</td>
                  <td>{o.date}</td>
                  <td className="price-col">{o.amount}</td>
                  <td>
                    <span className={`status-badge ${o.status === 'მიწოდებული' ? 'success' : o.status === 'გაგზავნილი' ? 'warning' : 'pending'}`}>
                      {o.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}