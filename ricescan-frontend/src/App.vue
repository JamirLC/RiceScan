<template>
  <div id="app">
    <header>
      <h1>RiceScan</h1>
    </header>

    <main>
      <!----- VIDEO STREAM -----> 
      <div class="video-container">
        <video ref="video" autoplay playsinline></video>
        <canvas ref="canvas" style="display: none;"></canvas>
      </div>

      <!----- CAPTURE & UPLOAD BUTTONS ----->
      <div class="controls">
        <button class="capture-btn" @click="captureImage">📷 Capture Image</button>
        <button class="upload-btn" @click="uploadImage">📁 Upload Image</button>
      </div>

      <!----- PREDICTION ----->
      <div class="result">
        <h2>{{ resultMessage }}</h2>
      </div>

      <!----- FILE UPLOAD SECTION ----->
      <div v-if="image" class="upload-section">
        <input type="file" @change="handleFileUpload" />
        <button @click="predictRiceType">Predict Rice Type</button>
        <p v-if="predictedClass">Predicted Rice Type: {{ predictedClass }}</p>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
// import { Camera } from '@capacitor/camera';  // USE THIS IF USING CAPACITOR
import { Permissions } from '@capacitor/core';

export default {
  data() {
    return {
      resultMessage: "Rice type will be displayed here.",
      videoStream: null,
      image: null,
      predictedClass: null,
      errorMessage: null,
      riceClasses: [],
      cameraErrorMessage: null,
    };
  },

  ///// METHODS /////
  methods: {
  
  ///// CAMERA FOR WEB /////
  async initCamera() {
    // WEB PERMISSION (CAMERA)
    if (navigator.mediaDevices) {
      try {
        await this.setupCamera();
      } catch (error) {
        console.error("Error accessing camera:", error);
        this.cameraErrorMessage = "Unable to access camera. Please check permissions.";
      }
    } else {
      this.cameraErrorMessage = "Camera API is not supported in this browser.";
    }
  },

  ///// CHECK CAMERA /////
  async setupCamera() {
    try {
      const videoStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });

     // VIDEO CAM STREAM //
     this.$refs.video.srcObject = videoStream;
     this.$refs.video.play();
    
    } catch (error) {
     console.error("Error accessing camera:", error);
     this.cameraErrorMessage = "Unable to access camera. Please check permissions.";
    }
  },

  isMobileDevice() {
    return /Mobi|Android/i.test(navigator.userAgent);
  },

  ///// CAMERA PERMISSION (MOBILE) /////
  async requestMobileCameraPermission() {
    const permission = await Permissions.request({ name: 'camera' });

    if (permission.granted) {
      this.setupCamera();
    } else {
      this.cameraErrorMessage = "Camera permission denied. Please allow access.";
    }
  },

  ///// UPLOAD DATA URL /////
  dataURLtoFile(dataURL, filename) {
    if (!dataURL || !dataURL.includes(',')) {
      console.error("Invalid or empty base64 string.");
      return null;
    }

    const [header, base64Data] = dataURL.split(',');
    
    if (!base64Data) {
      console.error("Base64 data is missing.");
      return null;
    }
    const mimeType = header.match(/:(.*?);/)[1];
    const binaryString = atob(base64Data);
    const length = binaryString.length;
    const arrayBuffer = new ArrayBuffer(length);
    const uint8Array = new Uint8Array(arrayBuffer);
    
    for (let i = 0; i < length; i++) {
      uint8Array[i] = binaryString.charCodeAt(i);
    }

    return new File([arrayBuffer], filename, { type: mimeType });
  },

  ///// IMAGE CAPTURING /////
  async captureImage() {
    const canvas = this.$refs.canvas;
    const video = this.$refs.video;
    const context = canvas.getContext("2d");
    const dataURL = canvas.toDataURL("image/jpeg");
    const imageFile = this.dataURLtoFile(dataURL, "captured-image.jpg");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    if (imageFile) {
       const formData = new FormData();
       formData.append("image", imageFile);

       try {
        console.log("Sending image to backend...");

        const response = await axios.post("http://localhost:5000/classify-rice", formData, {
          headers: {
          "Content-Type": "multipart/form-data",
          },
        });

        const result = response.data.result;
        console.log("Prediction result:", result);

         // DISPLAYS RESULTS ON FRONT-END
        if (result === "Rice type cannot be classified") {
          this.resultMessage = "Cannot identify rice.";
        } else {
          this.predictedClass = result;
          this.resultMessage = `Predicted Rice Type: ${this.predictedClass}`;
        }
      } catch (error) {
        console.error("Error during prediction:", error);
        this.errorMessage = "Failed to classify the rice. Please try again.";
      }
    } else {
      console.error("Failed to capture image.");
    }
  },

  ///// PREDICT RICE /////
  async uploadImage() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = async (event) => {
      const file = event.target.files[0];
      if (file) {
        const imageBitmap = await createImageBitmap(file);
        const canvas = this.$refs.canvas;
        const context = canvas.getContext("2d");
        canvas.width = imageBitmap.width;
        canvas.height = imageBitmap.height;
        context.drawImage(imageBitmap, 0, 0);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        this.processImage(imageData);
      }
    };
    input.click();
  },

  ///// IMAGE PROCESSING /////
  async processImage(imageData) {
    try {
      const resized = this.resizeImage(imageData);
      await this.sendImageForPrediction(resized);
    } catch (error) {
      console.error("Error processing image:", error);
      this.resultMessage = "Failed to process image.";
    }
  },

  resizeImage(imageData) {
    const canvas = this.$refs.canvas;
    const context = canvas.getContext("2d");
    canvas.width = 224;
    canvas.height = 224;
    context.putImageData(imageData, 0, 0);
    return canvas.toDataURL("image/jpeg");
  },

  ///// IMAGE PREDICTION PROCESSOR /////
  async sendImageForPrediction(imageBase64) {
    const formData = new FormData();
    formData.append("image", imageBase64);
    try {
      const response = await axios.post("http://localhost:5000/classify-rice", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const result = response.data.result;

      if (result === "Rice type cannot be classified") {
        this.resultMessage = "Cannot identify rice.";
      } else {
        this.predictedClass = result;
        this.resultMessage = `Predicted Rice Type: ${this.predictedClass}`;
      }
    } catch (error) {
      console.error(error);
      this.errorMessage = "Failed to classify the rice. Please try again.";
    }
  },

  ///// GET RICE TYPE /////
  async getRiceClasses() {
    try {
      const response = await axios.get("http://localhost:5000/get-rice-classes");
      this.riceClasses = response.data;
    } catch (error) {
      console.error("Error fetching rice classes:", error);
      this.riceClasses = [];
    }
  },

  ///// FILE UPLOAD /////
  handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
      this.image = file;
    }
  },

  ///// PREDICT RICE /////
  async predictRiceType() {
    if (!this.image) {
      this.errorMessage = "Please upload an image.";
      return;
    }

    const formData = new FormData();
    formData.append("image", this.image);

    try {
      const response = await axios.post("http://127.0.0.1:5000/classify-rice", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      // LOG SCRIPT
      console.log("Backend Response:", response.data);

      const result = response.data.result;

      if (result === "Rice type cannot be classified") {
        this.resultMessage = result; 
      } else {
        this.predictedClass = result;  // PREDICTED RICE RESULTS
        this.resultMessage = `Predicted Rice Type: ${this.predictedClass}`;
      }

      this.errorMessage = null;
      } catch (error) {
        console.error("Error uploading and classifying image:", error);
        this.errorMessage = "Failed to upload and classify the image.";
      }
    },
  },

  mounted() {
    this.initCamera();
    this.getRiceClasses();
  }
};
</script>

<style scoped>
/* Global Styles */
body {
  margin: 0;
  font-family: 'Arial', sans-serif;
  background-color: #f4f4f4;
  color: #333;
  padding: 10px;
  box-sizing: border-box;
}

/* Header */
header {
  background-color: #4caf50;
  padding: 10px;
  text-align: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

/* Main */
main {
  padding: 10px;
  text-align: center;
}

.video-container {
  position: relative;
  width: 100%;
  max-width: 320px;
  margin: 0 auto;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

video {
  width: 100%;
  height: auto;
}

/* Buttons */
.controls {
  margin-top: 15px;
}

button {
  width: 85%;
  max-width: 240px;
  margin: 10px auto;
  padding: 12px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.capture-btn {
  background-color: #4caf50;
  color: white;
}

.upload-btn {
  background-color: #2196f3;
  color: white;
}

button:hover {
  transform: translateY(-2px);
}

button:active {
  transform: translateY(1px);
}

/* Result */
.result {
  margin-top: 20px;
}

.result h2 {
  font-size: 18px;
  color: #555;
}

/* File Upload Section */
.upload-section {
  margin-top: 20px;
}

/* Error messages */
#errorMessage {
  color: red;
}

/* Mobile Responsiveness */
@media screen and (max-width: 600px) {
  header {
    font-size: 20px;
  }

  button {
    font-size: 14px;
    padding: 10px;
  }

  .result h2 {
    font-size: 16px;
  }

  .video-container {
    max-width: 280px;
  }
}
</style>
