import tensorflow as tf

model = tf.keras.models.load_model("rice_classifier_model.h5")

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("rice_classifier_model.tflite", "wb") as f:
    f.write(tflite_model)

print("Model converted to TensorFlow Lite format and saved as rice_classifier_model.tflite")
