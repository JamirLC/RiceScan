import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from tensorflow.keras.models import load_model
from PIL import Image
from django.conf import settings
import numpy as np
import os

# Set up logging
logger = logging.getLogger(__name__)

# Load model and rice classes globally, so it's loaded only once
model_path = os.path.join(settings.BASE_DIR, '..', 'rice_classifier_model.keras')
dataset_path = os.path.join(settings.BASE_DIR, '..', 'dataset')

print("Loading model from:", model_path)
model = load_model(model_path)

# Assuming the dataset folder contains class directories
rice_classes = os.listdir(dataset_path)

def index(request):
    index_path = os.path.join(settings.FRONTEND_BUILD_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HttpResponse(f.read())
    else:
        return HttpResponse("Frontend build not found.", status=500)

@api_view(['POST'])
def classify_rice(request):
    try:
        # Check if the 'image' key is in the uploaded files
        if 'image' not in request.FILES:
            return JsonResponse({"result": "No image file found."}, status=400)

        # Handle image file upload
        image_file = request.FILES['image']
        image = Image.open(image_file)
        image = image.resize((224, 224))  # Resize image to fit the model input
        image = np.array(image) / 255.0  # Normalize image data
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        # Predict rice type
        prediction = model.predict(image)
        predicted_class_index = np.argmax(prediction)  # Get the class with the highest probability
        predicted_class = rice_classes[predicted_class_index]  # Map to class label

        return JsonResponse({"result": f"Predicted Rice Type: {predicted_class}"})

    except Exception as e:
        # Log the error
        logger.error(f"Error processing the image: {str(e)}")
        return JsonResponse({"result": "Error processing the image", "error": str(e)}, status=500)
