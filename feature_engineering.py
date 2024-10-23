import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.preprocessing import StandardScaler

from ml import linear_regression, logistic_regression


def grab_data() -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    # Fetch data
    data = fetch_california_housing(as_frame=True)
    X = data.data.to_numpy()  # type: ignore
    y = data.target.to_numpy()  # type: ignore
    return X, y, data.frame  # type: ignore


def labelize_MedHouseVal(row):
    if row["MedHouseVal"] < row["pred_MedHouseVal"]:
        val = 1
    elif row["MedHouseVal"] > row["pred_MedHouseVal"]:
        val = 0
    else:
        val = 0
    return val


def split_dataset(
    data: np.ndarray, labels: np.ndarray, test_size: float = 0.2, random_seed: int = 42
):
    # Set random seed for reproducibility
    if random_seed is not None:
        np.random.seed(random_seed)

    indices = np.arange(data.shape[0])
    np.random.shuffle(indices)

    # Split based on the test size
    split_idx = int(data.shape[0] * (1 - test_size))
    train_indices, test_indices = indices[:split_idx], indices[split_idx:]

    # Split the data and labels
    X_train, X_test = data[train_indices], data[test_indices]
    y_train, y_test = labels[train_indices], labels[test_indices]

    return X_train, X_test, y_train, y_test


def logistic_regression_prediction(
    X: np.ndarray, y: np.ndarray, training_percentages: list
):
    scale = StandardScaler()
    X = scale.fit_transform(X)
    lor_hp = {"alpha": 0.08, "tau": 1e-4, "max_iter": 1000}
    rtn_val = []
    for pct in training_percentages:
        test_size = 1 - pct
        indices = np.arange(X.shape[0])
        # Split based on the test size
        split_idx = int(X.shape[0] * (1 - test_size))
        train_indices, test_indices = indices[:split_idx], indices[split_idx:]

        # Split the features and labels
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]

        lor = logistic_regression(lor_hp)
        lor.train(X_train, y_train)
        labels = lor.predict(X_test)
        rtn_val.append((labels, y_test))

    return rtn_val


def feature_engineering():
    X, y, data = grab_data()

    # Training
    reg_hp = {"type": 2, "lambda": 0.1}
    reg_lr = linear_regression(reg_hp)
    reg_lr.train(X, y)

    # Predicting
    pred_y = reg_lr.predict(X)

    # Append new Column
    data["pred_MedHouseVal"] = pred_y
    data["willing_to_purchase"] = data.apply(labelize_MedHouseVal, axis=1)

    # Check number of 1 and 0
    num_o_1 = len(data[data["willing_to_purchase"] == 1])
    num_o_0 = len(data[data["willing_to_purchase"] == 0])
    percentage_1 = (num_o_1 / (num_o_1 + num_o_0)) * 100
    percentage_0 = 100 - percentage_1
    print(f"\n number of 1: {num_o_1}, number of 0: {num_o_0} \n")
    print(f"precentage of 1: {percentage_1:.2f}% \n")
    print(f"precentage of 0: {percentage_0:.2f}% \n")

    # logistic_regression prediction
    y_true = data["willing_to_purchase"].to_numpy()
    training_percentages = [0.1, 0.2, 0.4, 0.6, 0.8, 0.999]
    pred_labels_list = logistic_regression_prediction(X, y_true, training_percentages)
    print()
    # Create a figure with 6 subplots (2 rows, 3 columns)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Loop through each set of predictions and plot the confusion matrix
    for i, labels in enumerate(pred_labels_list):
        cm = confusion_matrix(labels[0], labels[1])
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)

        # Determine which subplot to use (row and column indices)
        row, col = divmod(i, 3)
        disp.plot(ax=axes[row, col], cmap=plt.cm.Blues)
        axes[row, col].set_title(f"Used {training_percentages[i]}% for Training")

    # Adjust layout
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    feature_engineering()
