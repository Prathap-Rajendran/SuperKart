
# Import necessary libraries
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask application
product_sale_predictor_api = Flask("Product Sale Predictor")

# Load the trained machine learning model
model = joblib.load("product_sale_prediction_model_v1_0.joblib")


# Define a route for the home page (GET request)
@product_sale_predictor_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/').
    It returns a simple welcome message.
    """
    return "Welcome to the Product Store Sales Prediction API!"


# Define an endpoint for single product-store sales prediction
@product_sale_predictor_api.post('/v1/productsale')
def predict_product_sale():
    """
    This function handles POST requests to the '/v1/productsale' endpoint.

    It expects a JSON payload containing product and store details
    and returns the predicted Product Store Sales Total.
    """

    # Get the JSON data from the request body
    product_data = request.get_json()

    # Extract the features used by the trained model
    sample = {
        'Product_Weight': product_data['Product_Weight'],
        'Product_Sugar_Content': product_data['Product_Sugar_Content'],
        'Product_Allocated_Area': product_data['Product_Allocated_Area'],
        'Product_Type': product_data['Product_Type'],
        'Product_MRP': product_data['Product_MRP'],
        'Store_Id': product_data['Store_Id'],
        'Store_Size': product_data['Store_Size'],
        'Store_Location_City_Type': product_data['Store_Location_City_Type'],
        'Store_Type': product_data['Store_Type'],
        'Store_Age': product_data['Store_Age']
    }

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make prediction
    predicted_sale = model.predict(input_data)[0]

    # Convert prediction to Python float
    predicted_sale = round(float(predicted_sale), 2)

    # Return the prediction
    return jsonify({
        'Predicted Product Store Sales Total': predicted_sale
    })


# Define an endpoint for batch prediction
@product_sale_predictor_api.post('/v1/productsalebatch')
def predict_product_sale_batch():
    """
    This function handles POST requests to the '/v1/productsalebatch' endpoint.

    It expects a CSV file containing product and store features
    and returns predicted Product Store Sales Total for each row.
    """

    # Get the uploaded CSV file
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for all rows
    predicted_sales = model.predict(input_data).tolist()

    # Round predictions
    predicted_sales = [
        round(float(sale), 2)
        for sale in predicted_sales
    ]

    # Create output dictionary using Product_Id as the identifier
    if 'Product_Id' in input_data.columns:
        product_ids = input_data['Product_Id'].tolist()
        output_dict = dict(zip(product_ids, predicted_sales))
    else:
        output_dict = {
            str(i + 1): prediction
            for i, prediction in enumerate(predicted_sales)
        }

    # Return predictions
    return jsonify(output_dict)
