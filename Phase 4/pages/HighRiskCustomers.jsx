import { useEffect, useState } from "react";
import axios from "axios";
import BASE_URL from "../api";

function HighRiskCustomers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [limit, setLimit] = useState(50);
  const [sortOrder, setSortOrder] = useState("asc");

  const fetchCustomers = async (currentLimit) => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.get(
        `${BASE_URL}/customers/high-risk?limit=${currentLimit}`,
        {
          headers: {
            "x-api-key": "my-secret-key",
          },
        }
      );

      setCustomers(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load high-risk customers.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers(limit);
  }, [limit]);

  const handleLoadMore = () => {
    setLimit((prev) => prev + 50);
  };

  const handleSort = () => {
    const newOrder =
      sortOrder === "asc" ? "desc" : "asc";

    setSortOrder(newOrder);

    const sorted = [...customers].sort((a, b) =>
      newOrder === "asc"
        ? a.tenure - b.tenure
        : b.tenure - a.tenure
    );

    setCustomers(sorted);
  };

  if (loading) {
    return <h2>Loading...</h2>;
  }

  if (error) {
    return (
      <h2 style={{ color: "red" }}>
        {error}
      </h2>
    );
  }

  if (customers.length === 0) {
    return (
      <h2>No high-risk customers found</h2>
    );
  }

  return (
    <div>
      <h1>High-Risk Customers</h1>

      <p>
        Customers identified through business
        rules as having a higher likelihood of
        churn.
      </p>

      <div
        style={{
          backgroundColor: "#fff7e6",
          padding: "12px",
          borderRadius: "8px",
          marginBottom: "20px",
          fontWeight: "bold",
        }}
      >
        {customers.length} high-risk customers
        identified
      </div>

      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr>
            <th
              style={headerStyle}
            >
              Customer ID
            </th>

            <th
              style={{
                ...headerStyle,
                cursor: "pointer",
              }}
              onClick={handleSort}
            >
              Tenure{" "}
              {sortOrder === "asc"
                ? "▲"
                : "▼"}
            </th>

            <th style={headerStyle}>
              Monthly Charges
            </th>

            <th style={headerStyle}>
              Contract Type
            </th>

            <th style={headerStyle}>
              Risk Reason
            </th>
          </tr>
        </thead>

        <tbody>
          {customers.map((customer) => (
            <tr key={customer.customer_id}>
              <td style={cellStyle}>
                {customer.customer_id}
              </td>

              <td style={cellStyle}>
                {customer.tenure}
              </td>

              <td style={cellStyle}>
                $
                {customer.monthly_charges.toFixed(
                  2
                )}
              </td>

              <td style={cellStyle}>
                {customer.contract_type}
              </td>

              <td style={cellStyle}>
                {customer.risk_reason}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <button
        onClick={handleLoadMore}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          cursor: "pointer",
        }}
      >
        Load More
      </button>
    </div>
  );
}

const headerStyle = {
  border: "1px solid #ddd",
  padding: "10px",
  backgroundColor: "#f5f5f5",
};

const cellStyle = {
  border: "1px solid #ddd",
  padding: "10px",
};

export default HighRiskCustomers;