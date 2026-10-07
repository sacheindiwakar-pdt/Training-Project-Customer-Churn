import os
import joblib
import pandas as pd

from sqlalchemy import create_engine

from sklearn.model_selection import (
    train_test_split,
    cross_val_score
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support
)

# -----------------------------------------
# Database
# -----------------------------------------

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(DATABASE_URL)

# -----------------------------------------
# Load Features
# -----------------------------------------

df = pd.read_sql(
    "SELECT * FROM customer_ml_features",
    engine
)

print("\nDataset Shape")
print(df.shape)

# -----------------------------------------
# Target
# -----------------------------------------

y = df["churn"]

# -----------------------------------------
# Features
# -----------------------------------------

X = df.drop(
    columns=[
        "customer_id",
        "churn"
    ]
)

# -----------------------------------------
# One-Hot Encoding
# -----------------------------------------

X = pd.get_dummies(
    X,
    columns=[
        "contract_type",
        "internet_service"
    ],
    drop_first=False
)

print("\nX Shape")
print(X.shape)

print("\ny Shape")
print(y.shape)

# -----------------------------------------
# Train Test Split
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

# -----------------------------------------
# Models
# -----------------------------------------

log_model = LogisticRegression(
    max_iter=1000
)

tree_model = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)

# -----------------------------------------
# Train
# -----------------------------------------

log_model.fit(
    X_train,
    y_train
)

tree_model.fit(
    X_train,
    y_train
)

# -----------------------------------------
# Predict
# -----------------------------------------

log_pred = log_model.predict(
    X_test
)

tree_pred = tree_model.predict(
    X_test
)

# -----------------------------------------
# Logistic Report
# -----------------------------------------

print("\n" + "=" * 60)
print("LOGISTIC REGRESSION")
print("=" * 60)

print(
    classification_report(
        y_test,
        log_pred,
        target_names=[
            "Active",
            "Churned"
        ]
    )
)

print("Confusion Matrix")

print(
    confusion_matrix(
        y_test,
        log_pred
    )
)

# -----------------------------------------
# Tree Report
# -----------------------------------------

print("\n" + "=" * 60)
print("DECISION TREE")
print("=" * 60)

print(
    classification_report(
        y_test,
        tree_pred,
        target_names=[
            "Active",
            "Churned"
        ]
    )
)

print("Confusion Matrix")

print(
    confusion_matrix(
        y_test,
        tree_pred
    )
)

# -----------------------------------------
# Cross Validation
# -----------------------------------------

log_cv_f1 = cross_val_score(
    log_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

tree_cv_f1 = cross_val_score(
    tree_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

print("\nCV F1 Scores")

print(
    f"Logistic : {log_cv_f1.mean():.4f}"
)

print(
    f"Tree     : {tree_cv_f1.mean():.4f}"
)

# -----------------------------------------
# Metrics Helper
# -----------------------------------------

def model_metrics(
    y_true,
    y_pred,
    cv_f1
):

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            average=None
        )
    )

    return [
        round(accuracy, 4),
        round(precision[1], 4),
        round(recall[1], 4),
        round(f1[1], 4),
        round(cv_f1, 4)
    ]


# -----------------------------------------
# Comparison Table
# -----------------------------------------

comparison = pd.DataFrame(
    [
        [
            "Logistic Regression",
            *model_metrics(
                y_test,
                log_pred,
                log_cv_f1.mean()
            )
        ],

        [
            "Decision Tree",
            *model_metrics(
                y_test,
                tree_pred,
                tree_cv_f1.mean()
            )
        ]
    ],
    columns=[
        "Model",
        "Accuracy",
        "Precision (Churned)",
        "Recall (Churned)",
        "F1 (Churned)",
        "CV F1"
    ]
)

print("\nMODEL COMPARISON")

print(comparison)

# -----------------------------------------
# Pick Best Model
# -----------------------------------------

log_f1 = comparison.loc[
    comparison["Model"] ==
    "Logistic Regression",
    "F1 (Churned)"
].iloc[0]

tree_f1 = comparison.loc[
    comparison["Model"] ==
    "Decision Tree",
    "F1 (Churned)"
].iloc[0]

print("\nMODEL SELECTION")

if log_f1 >= tree_f1:

    best_model = "Logistic Regression"

    print(
        f"""
Best Model: {best_model}

Reason:
Chosen because it achieved the higher
F1 score for the Churned class.
F1 balances precision and recall and
is preferred over accuracy for an
imbalanced churn dataset.
"""
    )

else:

    best_model = "Decision Tree"

    print(
        f"""
Best Model: {best_model}

Reason:
Chosen because it achieved the higher
F1 score for the Churned class.
F1 balances precision and recall and
is preferred over accuracy for an
imbalanced churn dataset.
"""
    )

# -----------------------------------------
# Save Models
# -----------------------------------------

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    log_model,
    "models/logistic_churn.pkl"
)

joblib.dump(
    tree_model,
    "models/tree_churn.pkl"
)

print("\nModels Saved")

print(
    "models/logistic_churn.pkl"
)

print(
    "models/tree_churn.pkl"
)
import joblib

joblib.dump(
    X.columns.tolist(),
    "models/feature_columns.pkl"
)