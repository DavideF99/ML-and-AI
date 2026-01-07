# Pro-Grade Iris Classification: A "Data-First" Pipeline

This repository contains a supervised learning project targeting the classification of Iris species. While the Iris dataset is a common entry point, this project distinguishes itself by applying **production-level discipline**: rigorous data splitting, leak-proof feature scaling, and automated hyperparameter optimization.

## 🧠 Project Philosophy
In industry, 80% of performance gains come from data integrity, not "cooler" algorithms. This project implements:
1.  **Strict Data Separation**: Using a "Vault" (Holdout Test Set) strategy.
2.  **Zero Data Leakage**: Implementing Scikit-Learn `Pipelines` to ensure scaling parameters are learned only from training folds.
3.  **Baseline Validation**: Proving model value against a `DummyClassifier`.
4.  **Robustness**: Handling potential outliers via `IsolationForest`.



[Image of machine learning workflow diagram]


## 🛠️ Technical Implementation

### 1. Data Disciplines
* **Stratified Splitting**: Ensured class balance across the Training set and a 20% Test set using `stratify=y`.
* **Outlier Detection**: Implemented `IsolationForest` to identify and remove anomalous data points that could bias the decision boundaries.
* **Feature Engineering**: Identified **Petal Length** and **Petal Width** as the primary drivers of model performance using Random Forest `feature_importances_`.

### 2. The Pipeline Architecture
To prevent data leakage, all preprocessing and modeling steps were encapsulated in a `Pipeline`. This ensures that during cross-validation, the `StandardScaler` only "sees" the training folds:
* **Step 1: Scaling** (`StandardScaler`)
* **Step 2: Classifier** (SVM or Random Forest)



### 3. Model Optimization
I utilized `GridSearchCV` with 5-fold cross-validation to tune hyperparameters:
* **SVM**: Optimized `C` (regularization) and `kernel` (linear vs. RBF).
* **Random Forest**: Optimized `n_estimators` (tree count) and `max_depth`.

## 📊 Performance Results

### Final Test Set Metrics (The "Vault" Results)
| Model | Accuracy | 
| :--- | :--- |
| **Baseline (Dummy)** | 35.97% |
| **Logistic Regression** | 100.0% |
| **SVM (Optimized)** | 100.00% |
| **Random Forest** | 100.00% |

### Error Analysis & Visualization
The side-by-side Confusion Matrices show that the models perform perfectly on *Setosa*, with minor confusion occurring only between *Versicolor* and *Virginica*—a common challenge due to the physical overlap of these species. 


By visualizing the **Decision Boundaries** in the Petal feature space, we can observe the "Maximum Margin" logic of the SVM versus the "Heuristic Splits" of the Random Forest.


## 📂 Repository Structure
* `classifying_iris.ipynb`: The complete development notebook.
* `README.md`: Project documentation and results summary.

---

### How to use this project
1. Clone the repo.
2. Install dependencies: `pip install scikit-learn matplotlib pandas seaborn`
3. Run the notebook to reproduce the pipeline and plots.