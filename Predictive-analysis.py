import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Load the merged dataset
merged_df = pd.read_csv(r'C:\Users\kunnu\Desktop\COMP 8047\Data Sets\merged_traffic_weather_data.csv')

# Reduce sample size
merged_df = merged_df.sample(frac=0.5, random_state=42)

# Select relevant features for prediction
features = ['Hour', 'Month', 'actual_mean_temp', 'average_precipitation', 'DistanceToFirstStop_p50']

# Define the target variable
target = 'TotalTimeStopped_p50'

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(merged_df[features], merged_df[target], test_size=0.2, random_state=42)

print("Training set size:", X_train.shape[0])
print("Testing set size:", X_test.shape[0])

# Initialize the Linear Regression model
linear_model = LinearRegression()

# Train the Linear Regression model on the training data
linear_model.fit(X_train, y_train)

# Make predictions on the testing data using Linear Regression
y_pred_linear = linear_model.predict(X_test)

# Evaluate the Linear Regression model
mae_linear = mean_absolute_error(y_test, y_pred_linear)
rmse_linear = mean_squared_error(y_test, y_pred_linear, squared=False)

print("Linear Regression Model:")
print("Mean Absolute Error (MAE):", mae_linear)
print("Root Mean Squared Error (RMSE):", rmse_linear)

# Visualize feature importance for Linear Regression
feature_importance_linear = linear_model.coef_
plt.figure(figsize=(10, 6))
plt.barh(features, feature_importance_linear)
plt.xlabel('Feature Importance')
plt.ylabel('Feature')
plt.title('Feature Importance for Linear Regression')
plt.show()
plt.savefig('linear-regression.png')

# Initialize the Random Forest Regressor model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the Random Forest Regressor model on the training data
rf_model.fit(X_train, y_train)

# Make predictions on the testing data using Random Forest
y_pred_rf = rf_model.predict(X_test)

# Evaluate the Random Forest Regressor model
mae_rf = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = mean_squared_error(y_test, y_pred_rf, squared=False)

print("Random Forest Regressor Model:")
print("Mean Absolute Error (MAE):", mae_rf)
print("Root Mean Squared Error (RMSE):", rmse_rf)

# Visualize feature importance for Random Forest
feature_importance_rf = rf_model.feature_importances_
plt.figure(figsize=(10, 6))
plt.barh(features, feature_importance_rf)
plt.xlabel('Feature Importance')
plt.ylabel('Feature')
plt.title('Feature Importance for Random Forest Regressor')
plt.show()
plt.savefig('random-forest.png')

# Visualize predicted versus actual TotalTimeStopped_p50 values using scatter plot for Random Forest
plt.figure(figsize=(10, 6))
sns.scatterplot(x=y_test, y=y_pred_rf)
plt.xlabel('Actual TotalTimeStopped_p50')
plt.ylabel('Predicted TotalTimeStopped_p50')
plt.title('Actual vs. Predicted TotalTimeStopped_p50 (Random Forest Regressor)')
plt.show()
plt.savefig('actualVsPredicted.png')
