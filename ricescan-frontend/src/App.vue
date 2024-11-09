<template>
  <div id="app">
    <header>
      <h1>RiceScan</h1>
    </header>

    <main>
      <!-- Video Stream Container -->
      <div class="video-container">
        <video ref="video" autoplay playsinline></video>
        <canvas ref="canvas" style="display: none;"></canvas>
      </div>

      <!-- Controls for Capturing or Uploading an Image -->
      <div class="controls">
        <button class="capture-btn" @click="captureImage">📷 Capture Image</button>
        <button class="upload-btn" @click="uploadImage">📁 Upload Image</button>
      </div>

      <!-- Prediction Result -->
      <div class="result">
        <h2>{{ resultMessage }}</h2>
      </div>

      <!-- File Upload Section (optional for fallback) -->
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
      riceClasses: [],  // Store rice classes dynamically
      cameraErrorMessage: null,
    };
  },
  methods: {
    async initCamera() {
      try {
        this.videoStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" },
        });
        this.$refs.video.srcObject = this.videoStream;
        this.$refs.video.play();
      } catch (error) {
        console.error("Error accessing camera:", error);
        this.cameraErrorMessage = "Unable to access camera. Please check permissions.";
      }
    },
    
    async captureImage() {
      const video = this.$refs.video;
      const canvas = this.$refs.canvas;
      const context = canvas.getContext("2d");

      // Set canvas size to match video stream size
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw the current frame from video to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to a base64-encoded image (JPEG format)
      const imageData = canvas.toDataURL('image/jpeg');  // You can also use 'image/png' if needed

      // Convert base64 string to a file object
      const formData = new FormData();
      formData.append("image", this.dataURLtoFile(imageData, "captured_image.jpg"));

      // Send the image to the server
      try {
        const response = await axios.post("http://127.0.0.1:5000/classify-rice", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        
        console.log("Backend Response:", response.data);  // Handle server response (e.g., classification result)
        const result = response.data.result;

        if (result === "Rice type cannot be classified") {
          this.resultMessage = result;  // Display the fallback message
        } else {
          this.predictedClass = result;  // Display the predicted rice type
          this.resultMessage = `Predicted Rice Type: ${this.predictedClass}`; // Show result on the page
        }

        this.errorMessage = null;
      } catch (error) {
        console.error("Error uploading image:", error);
        this.errorMessage = "Failed to upload and classify the image.";
      }
    },

    // Helper function to convert base64 string to a file object
    dataURLtoFile(dataURL, filename) {
      const [header, base64Data] = dataURL.split(',');
      const mimeType = header.match(/:(.*?);/)[1];  // Extract MIME type (e.g., image/jpeg)
      const binaryString = atob(base64Data);
      const length = binaryString.length;
      const arrayBuffer = new ArrayBuffer(length);
      const uint8Array = new Uint8Array(arrayBuffer);

      // Convert base64 string to binary data
      for (let i = 0; i < length; i++) {
        uint8Array[i] = binaryString.charCodeAt(i);
      }

      return new File([arrayBuffer], filename, { type: mimeType });
    },

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

    async processImage(imageData) {
      try {
        const resized = this.resizeImage(imageData);
        this.sendImageForPrediction(resized);
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

    async sendImageForPrediction(imageBase64) {
      const formData = new FormData();
      formData.append("image", imageBase64);

      try {
        const response = await axios.post("http://localhost:5000/classify-rice", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        const result = response.data.result;

        if (result === "Rice type cannot be classified") {
          this.resultMessage = result;  // Display fallback message
        } else {
          this.predictedClass = result;
          this.resultMessage = `Predicted Rice Type: ${this.predictedClass}`;
        }
      } catch (error) {
        console.error(error);
        this.errorMessage = "Failed to classify the rice. Please try again.";
      }
    },

    //GET RICE CLASS
    async getRiceClasses() {
      try {
        const response = await axios.get("http://localhost:5000/get-rice-classes");
        this.riceClasses = response.data;
      } catch (error) {
        console.error("Error fetching rice classes:", error);
        this.riceClasses = [];
      }
    },

    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.image = file;
      }
    },

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

        // Log the backend response for debugging
        console.log("Backend Response:", response.data);

        const result = response.data.result;

        if (result === "Rice type cannot be classified") {
          this.resultMessage = result;  // Display the fallback message
        } else {
          this.predictedClass = result;  // Display the predicted rice type
          this.resultMessage = `Predicted Rice Type: ${this.predictedClass}`; // Show result on the page
        }

        this.errorMessage = null;
      } catch (error) {
        console.error(error);
        this.errorMessage = "Failed to classify the rice. Please try again.";
      }
    },
  },
  async mounted() {
    await this.getRiceClasses();
    await this.initCamera();
  },
  beforeUnmount() {
    if (this.videoStream) {
      this.videoStream.getTracks().forEach((track) => track.stop());
    }
  },
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
  width: 85%; /* Adjust button width for mobile */
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
