import os
from flask import Flask, request, jsonify, send_from_directory
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__, static_folder="ricescan-frontend/dist/static", template_folder="ricescan-frontend/dist")

CORS(app)

model = load_model("rice_classifier_model.keras")

# Dataset path and rice classes
dataset_path = "dataset"
rice_classes = os.listdir(dataset_path)  # Assuming the classes are in subdirectories within "dataset"

# Route to serve the index.html page (the main page of your Vue.js app)
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.template_folder), 'index.html')

# Route to serve rice classes (for the front-end to request them)
@app.route('/get-rice-classes', methods=['GET'])
def get_rice_classes():
    return jsonify(rice_classes)

# Route for handling the image prediction
@app.route('/classify-rice', methods=['POST'])
def classify_rice():
    try:
        # Get the image from the request
        file = request.files['image']
        image = Image.open(file.stream)

        # Preprocess the image for the model
        image = image.resize((224, 224))  # Adjust size for your model
        image = np.array(image) / 255.0  # Normalize
        image = np.expand_dims(image, axis=0)

        # Model prediction
        prediction = model.predict(image)
        predicted_class_index = np.argmax(prediction)
        predicted_class = rice_classes[predicted_class_index]

        print(f"Predicted Class: {predicted_class}")  # Log prediction result

        if predicted_class not in rice_classes:
            return jsonify({"result": "Rice type cannot be classified"})

        return jsonify({"result": predicted_class})

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"result": "Error processing the image"})

# FLASK SERVER
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
