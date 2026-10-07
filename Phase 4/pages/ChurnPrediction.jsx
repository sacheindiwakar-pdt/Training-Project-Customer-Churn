import { useState } from "react";
import axios from "axios";
import BASE_URL from "../api";

function ChurnPrediction() {
  const [formData, setFormData] = useState({
    tenure: "",
    monthly_charges: "",
    contract_type: "Month-to-month",
    service_count: "",
    internet_service: "DSL"
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [prediction, setPrediction] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const getRiskColor = (score) => {
    if (score < 0.3) return "#52c41a";
    if (score <= 0.6) return "#faad14";
    return "#ff4d4f";
  };

  const getConfidence = (score) => {
    if (score < 0.3) return "Low Risk";
    if (score <= 0.6) return "Medium Risk";
    return "High Risk";
  };

  const handleSubmit = async (e) => {
  e.preventDefault();

  setLoading(true);
  setError("");

  try {
    const response = await axios.post(
      `${BASE_URL}/predict-churn`,
      {
        tenure: Number(formData.tenure),
        monthly_charges: Number(formData.monthly_charges),
        contract_type: formData.contract_type,
        service_count: Number(formData.service_count),
        internet_service: formData.internet_service,
      },
      {
        headers: {
          "x-api-key": "my-secret-key",
        },
      }
    );

    setResult(response.data);
  } catch (err) {
    console.error(err);

    if (err.response?.status === 422) {
      const validationError =
        err.response.data.detail?.[0]?.msg ||
        "Validation error";

      setError(validationError);
    } else {
      setError("Unable to generate prediction.");
    }
  } finally {
    setLoading(false);
  }
};

  return (
    <div>
      <h1>Churn Prediction</h1>

      <p>
        Enter customer details to predict
        churn risk.
      </p>

      <form
        onSubmit={handleSubmit}
        style={{
          maxWidth: "500px",
          display: "flex",
          flexDirection: "column",
          gap: "15px",
        }}
      >
        <div>
          <label>Tenure</label>
          <input
            type="number"
            name="tenure"
            value={formData.tenure}
            onChange={handleChange}
            required
            min="0"
            max="100"
          />
        </div>

        <div>
          <label>Monthly Charges</label>
          <input
            type="number"
            name="monthly_charges"
            value={formData.monthly_charges}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Contract Type</label>

          <select
            name="contract_type"
            value={formData.contract_type}
            onChange={handleChange}
          >
            <option>
              Month-to-month
            </option>

            <option>
              One year
            </option>

            <option>
              Two year
            </option>
          </select>
        </div>
        <div>
          <label>Internet Service</label>

          <select
            name="internet_service"
          value={formData.internet_service}
          onChange={handleChange}
          >
            <option value="DSL">DSL</option>
            <option value="Fiber optic">Fiber optic</option>
            <option value="No">No</option>
          </select>
        </div>
        <div>
          <label>Service Count</label>
          <input
            type="number"
            name="service_count"
            value={formData.service_count}
            onChange={handleChange}
            required
            min="0"
            max="6"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Predicting..."
            : "Predict Churn"}
        </button>
      </form>

      {error && (
        <div
          style={{
            marginTop: "20px",
            color: "red",
          }}
        >
          {error}
        </div>
      )}

      {result && (
        <div
          style={{
            marginTop: "30px",
            padding: "20px",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          <h2>Prediction Result</h2>

          <p>
            <strong>Prediction:</strong>{" "}
            {result.prediction}
          </p>

          <p>
            <strong>Risk Score:</strong>{" "}
            {(result.risk_score * 100).toFixed(
              1
            )}
            %
          </p>

          <p>
            <strong>Confidence:</strong>{" "}
            {getConfidence(
              result.risk_score
            )}
          </p>

          <div
            style={{
              marginTop: "10px",
              height: "25px",
              width: "300px",
              backgroundColor: "#f0f0f0",
              borderRadius: "8px",
            }}
          >
            <div
              style={{
                width: `${
                  result.risk_score * 100
                }%`,
                height: "100%",
                backgroundColor:
                  getRiskColor(
                    result.risk_score
                  ),
                borderRadius: "8px",
              }}
            />
          </div>

          <p
            style={{
              marginTop: "15px",
              padding: "10px",
              backgroundColor:
                getRiskColor(
                  result.risk_score
                ),
              color: "white",
              display: "inline-block",
              borderRadius: "5px",
            }}
          >
            {result.prediction}
          </p>

          <p>
            <strong>Note:</strong>{" "}
            {result.note}
          </p>
        </div>
      )}
    </div>
  );
}

export default ChurnPrediction;