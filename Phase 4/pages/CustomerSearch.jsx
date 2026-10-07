import { useState } from "react";
import axios from "axios";
import BASE_URL from "../api";

function CustomerSearch() {
  const [customerId, setCustomerId] = useState("");
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchCustomer = async () => {
    if (!customerId.trim()) return;

    setLoading(true);
    setError("");
    setCustomer(null);

    try {
      const response = await axios.get(
        `${BASE_URL}/customer/${customerId}`,
        {
          headers: {
            "x-api-key": "my-secret-key",
          },
        }
      );

      setCustomer(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError("Customer not found");
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Customer Search</h2>

      <input
        type="text"
        placeholder="Enter Customer ID"
        value={customerId}
        onChange={(e) => setCustomerId(e.target.value)}
        style={{
          padding: "10px",
          width: "250px",
          marginRight: "10px",
        }}
      />

      <button onClick={searchCustomer}>
        Search
      </button>

      {loading && (
        <p>Loading...</p>
      )}

      {error && (
        <p style={{ color: "red" }}>
          {error}
        </p>
      )}

      {customer && (
        <div
          style={{
            marginTop: "20px",
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "15px",
            width: "400px",
            boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
          }}
        >
          <h3>{customer.customer_id}</h3>

          <p>
            <strong>Tenure:</strong>{" "}
            {customer.tenure}
          </p>

          <p>
            <strong>Contract:</strong>{" "}
            {customer.contract_type}
          </p>

          <p>
            <strong>Internet Service:</strong>{" "}
            {customer.internet_service}
          </p>

          <p>
            <strong>Monthly Charges:</strong> ₹
            {customer.monthly_charges}
          </p>

          <p>
            <strong>Status:</strong>{" "}
            <span
              style={{
                backgroundColor:
                  customer.churn === 1
                    ? "#ff4d4f"
                    : "#52c41a",
                color: "white",
                padding: "5px 10px",
                borderRadius: "6px",
              }}
            >
              {customer.churn === 1
                ? "Churned"
                : "Active"}
            </span>
          </p>
        </div>
      )}
    </div>
  );
}

export default CustomerSearch;