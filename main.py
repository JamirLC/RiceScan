import os
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img

class CameraBox(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraBox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.img = Image()
        self.add_widget(self.img)

        self.capture_button = Button(text="Capture Photo", size_hint=(1, 0.2))
        self.capture_button.bind(on_release=self.capture_image)
        self.add_widget(self.capture_button)

        self.result_label = Label(text="Rice type will be displayed here.", size_hint=(1, 0.1))
        self.add_widget(self.result_label)

        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30)

        # FOR PRE-TRAINED MODEL
        self.model = load_model("rice_classifier_model.keras")
        self.dataset_path = "dataset" 
        self.assets_folder = "assets"
        os.makedirs(self.assets_folder, exist_ok=True)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = texture

    def capture_image(self, *args):
        ret, frame = self.capture.read()
        if ret:
            # SAVE CAPTURED IMAGE
            filename = os.path.join(self.assets_folder, f"img_{int(Clock.get_time() * 1000)}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Image captured and saved as {filename}")
            
            resized_image_path = os.path.join(self.assets_folder, "resized_" + os.path.basename(filename))
            resized_frame = cv2.resize(frame, (224, 224)) 
            cv2.imwrite(resized_image_path, resized_frame)
            
            # RICE TYPE CLASSIFIER
            rice_type = self.classify_rice(resized_image_path)
            if rice_type:
                self.result_label.text = f"Scanned item: {rice_type} rice identified"
            else:
                self.result_label.text = "Rice can't be identified"

    def classify_rice(self, image_path):
        # CAPTURED IMAGE PROCESSOR
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        print(f"Shape of img_array: {img_array.shape}")

        # PREDICT THE TYPE OF RICE
        prediction = self.model.predict(img_array)
        rice_classes = os.listdir(self.dataset_path)  # FOLDER DIRECTORY NUNG RICE SAMPLES
        confidence_threshold = 0.6
        max_confidence = np.max(prediction)
        
        if max_confidence > confidence_threshold:
            predicted_class = rice_classes[np.argmax(prediction)]
            return predicted_class
        else:
            return None 

    def on_stop(self):
        self.capture.release()

class RiceScanApp(App):
    def build(self):
        return CameraBox()

if __name__ == '__main__':
    RiceScanApp().run()
