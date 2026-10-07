import { useEffect, useState } from "react";
import axios from "axios";
import BASE_URL from "../api";

function ChurnSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await axios.get(
          `${BASE_URL}/churn/summary`,
          {
            headers: {
              "x-api-key": "my-secret-key",
            },
          }
        );

        setSummary(response.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load churn summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

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

  return (
    <div>
      <h1>Churn Summary Dashboard</h1>

      <p>
        This dashboard provides an overview of customer churn and compares churn rates across contract types.
      </p>

      {/* Metric Cards */}

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "20px",
          marginBottom: "30px",
        }}
      >
        <div
          style={{
            padding: "20px",
            borderRadius: "8px",
            background: "#f0f2f5",
            minWidth: "200px",
          }}
        >
          <h3>Total Customers</h3>
          <h2>{summary.total_customers}</h2>
        </div>

        <div
          style={{
            padding: "20px",
            borderRadius: "8px",
            background: "#fff7e6",
            minWidth: "200px",
          }}
        >
          <h3>Total Churned</h3>
          <h2>{summary.total_churned}</h2>
        </div>

        <div
          style={{
            padding: "20px",
            borderRadius: "8px",
            background: "#f6ffed",
            minWidth: "200px",
          }}
        >
          <h3>Churn Rate</h3>
          <h2>
            {(summary.churn_rate * 100).toFixed(1)}%
          </h2>
        </div>
      </div>

      {/* Contract Table */}

      <h2>Churn by Contract Type</h2>

      <table
        border="1"
        cellPadding="10"
        style={{
          borderCollapse: "collapse",
          width: "100%",
        }}
      >
        <thead>
          <tr>
            <th>Contract Type</th>
            <th>Churn Rate</th>
            <th>Visual</th>
          </tr>
        </thead>

        <tbody>
          {summary.by_contract.map((item) => (
            <tr key={item.contract_type}>
              <td>{item.contract_type}</td>

              <td>
                {(item.churn_rate * 100).toFixed(1)}%
              </td>

              <td>
                <div
                  style={{
                    width: "250px",
                    backgroundColor: "#eee",
                    height: "20px",
                    borderRadius: "4px",
                  }}
                >
                  <div
                    style={{
                      width: `${item.churn_rate * 100}%`,
                      height: "20px",
                      backgroundColor: "#1677ff",
                      borderRadius: "4px",
                    }}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ChurnSummary;
