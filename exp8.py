import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

has_lstm = True
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
except Exception as ex:
    print("⚠️ TensorFlow/Keras unavailable: skipping LSTM training.", ex)
    has_lstm = False

# Objective: stock price prediction using ALL_Stocks_Data.csv + Linear Regression + LSTM

def load_symbol_from_all_stocks(symbol="3MINDIA", input_csv="ALL_Stocks_Data.csv"):
    df_all = pd.read_csv(input_csv)
    if "symbol" not in df_all.columns:
        raise ValueError("input CSV must have a 'symbol' column")

    selected = df_all[df_all["symbol"].astype(str).str.upper() == symbol.upper()]
    if selected.empty:
        raise ValueError(f"Symbol '{symbol}' not found in {input_csv}")

    # For this format, each row has all close values as separate date-based columns after symbol:
    # [unnamed index, symbol, date1, date2, ...]
    row = selected.iloc[0]
    values = row.drop(labels=["symbol"]).values
    prices = pd.to_numeric(values, errors="coerce")
    prices = prices[~np.isnan(prices)]

    if len(prices) < 30:
        raise ValueError(f"Not enough values for {symbol} (found {len(prices)})")

    # Some date order appears reverse chronological; sort to chronological by using the column order
    prices = prices[::-1]
    out_df = pd.DataFrame({"Close": prices})
    out_df.index.name = "Date"
    return out_df

print("Loading ALL_Stocks_Data.csv for 3MINDIA...")
df = load_symbol_from_all_stocks("3MINDIA")
print(df.head())

# Pre-process
df.dropna(inplace=True)
scaler = MinMaxScaler(feature_range=(0, 1))
df_scaled = scaler.fit_transform(df)

# Split
train_size = int(len(df_scaled) * 0.8)
train_data, test_data = df_scaled[:train_size], df_scaled[train_size:]

sequence_length = 10

# Linear Regression (time index)
X_train = np.arange(len(train_data)).reshape(-1, 1)
y_train = train_data.flatten()
X_test = np.arange(len(train_data), len(df_scaled)).reshape(-1, 1)
y_test = test_data.flatten()

lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

lr_predictions = lr_model.predict(X_test)
lr_predictions_inv = scaler.inverse_transform(lr_predictions.reshape(-1, 1)).flatten()

lr_mse = mean_squared_error(scaler.inverse_transform(test_data), lr_predictions_inv.reshape(-1, 1))
print(f"Linear Regression MSE: {lr_mse:.6f}")

meta = {
    "train_size": train_size,
    "total_length": len(df_scaled),
    "sequence_length": sequence_length
}
pickle.dump(meta, open("model_meta.pkl", "wb"))
np.save("lstm_window.npy", df_scaled[-sequence_length:])

pickle.dump(scaler, open("scaler.pkl", "wb"))
pickle.dump(lr_model, open("lr_model.pkl", "wb"))
print("Saved scaler and Linear Regression model.")

sequence_length = 10
lstm_model = None

if has_lstm and len(train_data) > sequence_length:

    def create_sequences(data, seq_len=10):
        X, y = [], []
        for i in range(len(data) - seq_len):
            X.append(data[i:i + seq_len])
            y.append(data[i + seq_len])
        return np.array(X), np.array(y)

    X_train_lstm, y_train_lstm = create_sequences(train_data, sequence_length)
    X_test_lstm, y_test_lstm = create_sequences(test_data, sequence_length)

    X_train_lstm = X_train_lstm.reshape((X_train_lstm.shape[0], sequence_length, 1))
    X_test_lstm = X_test_lstm.reshape((X_test_lstm.shape[0], sequence_length, 1))

    lstm_model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
        LSTM(50, return_sequences=False),
        Dense(25),
        Dense(1)
    ])

    lstm_model.compile(optimizer="adam", loss="mean_squared_error")
    lstm_model.fit(X_train_lstm, y_train_lstm, epochs=20, batch_size=16, verbose=1)

    lstm_predictions = lstm_model.predict(X_test_lstm)
    lstm_predictions_inv = scaler.inverse_transform(lstm_predictions)
    lstm_y_test_inv = scaler.inverse_transform(y_test_lstm.reshape(-1, 1))

    lstm_mse = mean_squared_error(lstm_y_test_inv, lstm_predictions_inv)
    print(f"LSTM MSE: {lstm_mse:.6f}")

    lstm_model.save("lstm_model.h5")
    print("Saved LSTM model to lstm_model.h5")

else:
    print("LSTM training skipped (no TF or insufficient data).")

print("✅ Models trained and saved successfully!")
