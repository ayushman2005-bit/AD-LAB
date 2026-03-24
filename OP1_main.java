package com.example.openend_project;

import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {

    EditText tableNumber;
    EditText customerName;
    EditText specialInstructions;
    Button sendButton;
    LinearLayout itemsContainer;

    OkHttpClient client = new OkHttpClient();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        tableNumber = findViewById(R.id.tableNumber);
        customerName = findViewById(R.id.customerName);
        specialInstructions = findViewById(R.id.specialInstructions);
        sendButton = findViewById(R.id.sendButton);
        itemsContainer = findViewById(R.id.itemsContainer);
        Button addItemButton = findViewById(R.id.addItemButton);

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main),
                (v, insets) -> {
                    Insets systemBars =
                            insets.getInsets(WindowInsetsCompat.Type.systemBars());
                    v.setPadding(systemBars.left, systemBars.top, systemBars.right,
                            systemBars.bottom);
                    return insets;
                });

        // Add item row
        addItemButton.setOnClickListener(v -> {
            LinearLayout itemRow = new LinearLayout(this);
            itemRow.setOrientation(LinearLayout.HORIZONTAL);

            EditText itemName = new EditText(this);
            itemName.setHint("Item Name");
            itemName.setLayoutParams(new LinearLayout.LayoutParams(
                    0, ViewGroup.LayoutParams.WRAP_CONTENT, 3));

            EditText quantity = new EditText(this);
            quantity.setHint("Qty");
            quantity.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
            quantity.setLayoutParams(new LinearLayout.LayoutParams(
                    0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));

            itemRow.addView(itemName);
            itemRow.addView(quantity);
            itemsContainer.addView(itemRow);
        });

        // Send order button
        sendButton.setOnClickListener(v -> sendOrder());
    }

    void sendOrder() {
        try {
            String table = tableNumber.getText().toString();
            String customer = customerName.getText().toString();
            String instructions = specialInstructions.getText().toString();

            JSONArray itemsArray = new JSONArray();

            for (int i = 0; i < itemsContainer.getChildCount(); i++) {
                LinearLayout row = (LinearLayout) itemsContainer.getChildAt(i);
                EditText itemName = (EditText) row.getChildAt(0);
                EditText quantity = (EditText) row.getChildAt(1);

                JSONObject item = new JSONObject();
                item.put("name", itemName.getText().toString());
                item.put("qty", quantity.getText().toString());

                itemsArray.put(item);
            }

            JSONObject order = new JSONObject();
            order.put("table", table);
            order.put("customer", customer);
            order.put("instructions", instructions);
            order.put("items", itemsArray);

            MediaType JSON = MediaType.get("application/json; charset=utf-8");
            RequestBody body = RequestBody.create(order.toString(), JSON);

            Request request = new Request.Builder()
                    .url("http://10.5.98.59:5000/order") // CHANGE TO YOUR PC IP
                    .post(body)
                    .build();

            client.newCall(request).enqueue(new Callback() {

                @Override
                public void onFailure(Call call, IOException e) {
                    e.printStackTrace();
                }

                @Override
                public void onResponse(Call call, Response response) {
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this,
                                "Order Sent!", Toast.LENGTH_SHORT).show();
                        resetForm();
                    });
                }
            });

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    void resetForm() {
        tableNumber.setText("");
        customerName.setText("");
        specialInstructions.setText("");
        itemsContainer.removeAllViews();
    }
}
