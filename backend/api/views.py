import os
import numpy as np
import tensorflow as tf
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Define paths for the model and dataset
MODEL_PATH = r'D:\VSCODE\RiceScan\rice_classifier_model.keras'
DATASET_PATH = r'D:\VSCODE\RiceScan\augmentation'

# Load the model once when the server starts
model = tf.keras.models.load_model(MODEL_PATH)

@csrf_exempt
def classify_rice(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Save the uploaded image
        uploaded_file = request.FILES['image']
        file_path = default_storage.save(f"temp/{uploaded_file.name}", ContentFile(uploaded_file.read()))
        abs_file_path = os.path.join(default_storage.location, file_path)
        
        try:
            # Preprocess the image
            image = tf.keras.utils.load_img(abs_file_path, target_size=(224, 224))
            image_array = tf.keras.utils.img_to_array(image) / 255.0
            image_array = np.expand_dims(image_array, axis=0)

            # Predict the rice type
            predictions = model.predict(image_array)
            predicted_class = np.argmax(predictions[0])

            # Get the rice class name from dataset folder names
            class_names = sorted(os.listdir(DATASET_PATH))
            rice_type = class_names[predicted_class]

            # Respond with the prediction
            return JsonResponse({
                'success': True,
                'riceType': rice_type,
                'result': 'Rice type classified successfully.',
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        finally:
            # Clean up the temporary file
            if os.path.exists(abs_file_path):
                os.remove(abs_file_path)

    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)
