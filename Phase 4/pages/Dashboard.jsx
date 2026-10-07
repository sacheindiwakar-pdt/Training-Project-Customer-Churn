import { useEffect, useState } from "react";
import axios from "axios";
import BASE_URL from "../api";

function Dashboard() {
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
        setError("Failed to load data");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) return <h2>Loading...</h2>;

  if (error) return <h2>{error}</h2>;

  return (
    <div>
      <h2>Dashboard Summary</h2>

      <p>
        Total Customers: {summary.total_customers}
      </p>

      <p>
        Total Churned: {summary.total_churned}
      </p>

      <p>
        Churn Rate: {summary.churn_rate}
      </p>
    </div>
  );
}

export default Dashboard;