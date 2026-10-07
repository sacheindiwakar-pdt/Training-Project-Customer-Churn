import { useState } from "react";

import ChurnSummary from "./pages/ChurnSummary";
import CustomerSearch from "./pages/CustomerSearch";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";

function App() {
  const [activeTab, setActiveTab] = useState("summary");

  return (
    <div>
      <header
        style={{
          backgroundColor: "#1677ff",
          color: "white",
          padding: "20px",
        }}
      >
        <h1>Customer Churn Dashboard</h1>
      </header>

      <nav
        style={{
          padding: "15px",
          backgroundColor: "#f5f5f5",
          borderBottom: "1px solid #ddd",
        }}
      >
        <button
          onClick={() => setActiveTab("summary")}
          style={{
            marginRight: "10px",
            padding: "10px 15px",
            cursor: "pointer",
            backgroundColor:
              activeTab === "summary"
                ? "#1677ff"
                : "#e0e0e0",
            color:
              activeTab === "summary"
                ? "white"
                : "black",
            border: "none",
            borderRadius: "5px",
          }}
        >
          Churn Summary
        </button>

        <button
          onClick={() => setActiveTab("search")}
          style={{
            marginRight: "10px",
            padding: "10px 15px",
            cursor: "pointer",
            backgroundColor:
              activeTab === "search"
                ? "#1677ff"
                : "#e0e0e0",
            color:
              activeTab === "search"
                ? "white"
                : "black",
            border: "none",
            borderRadius: "5px",
          }}
        >
          Customer Search
        </button>

        <button
          onClick={() => setActiveTab("risk")}
          style={{
            padding: "10px 15px",
            cursor: "pointer",
            backgroundColor:
              activeTab === "risk"
                ? "#1677ff"
                : "#e0e0e0",
            color:
              activeTab === "risk"
                ? "white"
                : "black",
            border: "none",
            borderRadius: "5px",
          }}
        >
          High Risk Customers
        </button>
        <button
          onClick={() => setActiveTab("prediction")}
          style={{
          marginLeft: "10px",
          padding: "10px 15px",
        }}
>
        Churn Prediction
        </button>
      </nav>

      <main
        style={{
          padding: "20px",
        }}
      >
        {activeTab === "summary" && (
          <ChurnSummary />
        )}

        {activeTab === "search" && (
          <CustomerSearch />
        )}

        {activeTab === "risk" && (
          <HighRiskCustomers />

        )}

        {activeTab === "prediction" && (
          <ChurnPrediction />
        )}  
      </main>
    </div>
  );
}

export default App;