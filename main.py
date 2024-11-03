import os
import cv2
import numpy as np
import threading
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from skimage.metrics import structural_similarity as ssim

class CameraBox(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraBox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.img = Image()
        self.add_widget(self.img)
        self.result_label = Label(text="Rice type will be displayed here.", size_hint=(1, 0.1))
        self.add_widget(self.result_label)
        
        # CAPTURE BUTTON
        self.capture_button = Button(text="Capture Image", size_hint=(1, 0.1))
        self.capture_button.bind(on_press=self.capture_image)
        self.add_widget(self.capture_button)

        # UPLOAD BUTTON
        self.upload_button = Button(text="Upload Image", size_hint=(1, 0.1))
        self.upload_button.bind(on_press=self.open_file_chooser)
        self.add_widget(self.upload_button)

        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30)

        # LOAD PRE-TRAINED MODEL
        self.model = load_model("rice_classifier_model.keras")
        self.dataset_path = "dataset"
        
        # LOAD RICE TYPE FROM DATASET FOLDER
        self.rice_classes = os.listdir(self.dataset_path)

        # LOAD REFERENCE RICE TYPE
        self.reference_images = {}
        for rice_class in self.rice_classes:
            class_path = os.path.join(self.dataset_path, rice_class)
            sample_image_path = os.path.join(class_path, os.listdir(class_path)[0])  # LOAD THE FIRST IMAGE
            self.reference_images[rice_class] = cv2.imread(sample_image_path, cv2.IMREAD_GRAYSCALE)
        self.captured_frame = None

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            self.captured_frame = frame
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = texture

    def capture_image(self, instance):
        # CAPTURE IMAGE
        threading.Thread(target=self.process_image, args=(self.captured_frame,)).start()

    def open_file_chooser(self, instance):
        # FILE CHOOSER
        filechooser = FileChooserIconView(path="C:/Users/Owner/Desktop") #CHANGE DEPENDING ON WHERE YOU WANT TO START
        filechooser.filters = ["*.jpg", "*.jpeg", "*.png"]  # Display only image files

        # OK BUTTON
        ok_button = Button(text="Select", size_hint=(1, 0.1))
        ok_button.bind(on_release=lambda btn: self.on_file_selected(filechooser.selection))

        # Layout for FileChooser and OK button
        chooser_layout = BoxLayout(orientation="vertical")
        chooser_layout.add_widget(filechooser)
        chooser_layout.add_widget(ok_button)

        # FILE CHOOSER POP UP
        self.popup = Popup(title="Select an Image", content=chooser_layout, size_hint=(0.9, 0.9))
        self.popup.open()

    def on_file_selected(self, selection):
        if selection:
            image_path = selection[0]
            #print(f"File selected: {image_path}") for debugging langs
            uploaded_image = cv2.imread(image_path)
            if uploaded_image is not None:
                self.popup.dismiss() 
                threading.Thread(target=self.process_image, args=(uploaded_image,)).start()

    def process_image(self, frame):
        if frame is None:
            self.result_label.text = "Failed to capture or load image"
            return

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame_resized = cv2.resize(gray_frame, (100, 100))
        best_match_class = None
        highest_similarity = 0
        confidence_threshold = 0.6

        for rice_class in self.rice_classes:
            class_folder = os.path.join(self.dataset_path, rice_class)
            image_files = os.listdir(class_folder)
            sample_images = random.sample(image_files, min(5, len(image_files)))  # Select 5 random samples from each folder

            for image_file in sample_images:
                reference_image_path = os.path.join(class_folder, image_file)
                reference_image = cv2.imread(reference_image_path, cv2.IMREAD_GRAYSCALE)
                
                if reference_image is None:
                    continue

                reference_image_resized = cv2.resize(reference_image, (100, 100))
                similarity = ssim(gray_frame_resized, reference_image_resized)

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match_class = rice_class

        # DISPLAY THE HIGHEST SIMILARITY
        if highest_similarity > confidence_threshold:
            resized_frame = cv2.resize(frame, (224, 224))
            img_array = img_to_array(resized_frame) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            rice_type = self.classify_rice(img_array)
            self.result_label.text = f"Scanned item: {best_match_class} rice identified"
        else:
            self.result_label.text = "Uploaded image does not match sample rice images."

    def classify_rice(self, img_array):
        # PREDICTION
        prediction = self.model.predict(img_array)
        confidence_threshold = 0.6
        max_confidence = np.max(prediction)
        
        if max_confidence > confidence_threshold:
            predicted_class = self.rice_classes[np.argmax(prediction)]
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
