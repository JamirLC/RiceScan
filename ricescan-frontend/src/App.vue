<template>
  <div id="app">
    <header>
      <h1>RiceScan</h1>
    </header>

    <main>
      <!-- Video Stream -->
      <div class="video-container">
        <video ref="video" autoplay playsinline></video>
        <canvas ref="canvas" style="display: none;"></canvas>
      </div>

      <!-- Capture & Upload Buttons -->
      <div class="controls">
        <button class="capture-btn" @click="captureImage">📷 Capture Image</button>
        <button class="upload-btn" @click="uploadImage">📁 Upload Image</button>
      </div>

      <!-- Prediction -->
      <div class="result">
        <h2>{{ resultMessage }}</h2>
      </div>

      <!-- File Upload Section -->
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

  methods: {
    // Method to classify rice type by sending the image to the Django backend
    async classifyRice() {
      const formData = new FormData();
      formData.append("image", this.image);

      try {
        const response = await axios.post("http://localhost:8000/api/classify-rice/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        // Handle response from the backend
        this.resultMessage = response.data.result;

      } catch (error) {
        console.error("Error:", error);
        this.errorMessage = "Failed to classify the rice. Please try again.";
      }
    },

    // Method for capturing image from video stream
    async captureImage() {
      const canvas = this.$refs.canvas;
      const video = this.$refs.video;
      const context = canvas.getContext("2d");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Get the image data as a DataURL
      const dataURL = canvas.toDataURL("image/jpeg");

      // Convert DataURL to File
      this.image = this.dataURLtoFile(dataURL, "captured-image.jpg");

      // Create FormData and append the image
      const formData = new FormData();
      formData.append("image", this.image);

      // Send the image to the backend
      try {
        const response = await axios.post("http://localhost:8000/api/classify-rice/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        this.resultMessage = response.data.result;
      } catch (error) {
        console.error("Error:", error);
        this.errorMessage = "Failed to classify the rice. Please try again.";
      }
    },

    // Method to convert DataURL to file
    dataURLtoFile(dataURL, filename) {
      const [, base64Data] = dataURL.split(',');
      const binaryData = atob(base64Data);
      const arrayBuffer = new ArrayBuffer(binaryData.length);
      const uint8Array = new Uint8Array(arrayBuffer);

      for (let i = 0; i < binaryData.length; i++) {
        uint8Array[i] = binaryData.charCodeAt(i);
      }

      return new File([uint8Array], filename, { type: 'image/jpeg' });
    },

    // Handle file upload
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.image = file;
      }
    },

    // Method to handle file upload and prediction
    async predictRiceType() {
      if (!this.image) {
        this.errorMessage = "Please upload an image.";
        return;
      }

      await this.classifyRice();
    }
  },

  mounted() {
    // Initialization for starting video stream
    const video = this.$refs.video;
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        video.srcObject = stream;
      })
      .catch((error) => {
        console.error("Error accessing webcam: ", error);
        this.cameraErrorMessage = "Unable to access the camera.";
      });
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
