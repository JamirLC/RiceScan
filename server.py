import os
from flask import Flask, request, jsonify, send_from_directory
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from flask_cors import CORS

# FLASK APP (APP.VUE)
app = Flask(__name__, static_folder="ricescan-frontend/dist/static", template_folder="ricescan-frontend/dist")
CORS(app)

# TRAINED MODEL
model = load_model("rice_classifier_model.keras")

# DATASET PATH
dataset_path = "dataset"
rice_classes = os.listdir(dataset_path)

# INDEX.HTML ROUTE
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.template_folder), 'index.html')

# GET RICE CLASSES (FOR FRONT-END)
@app.route('/get-rice-classes', methods=['GET'])
def get_rice_classes():
    return jsonify(rice_classes)

# IMAGE PREDICTION ROUTE
@app.route('/classify-rice', methods=['POST'])
def classify_rice():
    try:
        # IMAGE REQUEST
        file = request.files['image']
        image = Image.open(file.stream)

        # MODEL PROCESS
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)

        # MODEL PREDICTION
        prediction = model.predict(image)
        predicted_class_index = np.argmax(prediction)
        predicted_class = rice_classes[predicted_class_index]

        print(f"Predicted Class: {predicted_class}")  # LOGS

        # IF STATEMENT (RICE CLASSES)
        if predicted_class not in rice_classes:
            return jsonify({"result": "Predicted Rice Type: None"})

        return jsonify({"result": f"Predicted Rice Type: {predicted_class}"})

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"result": "Error processing the image"})

# START FLASK SERVER
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
