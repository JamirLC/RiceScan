<template>
  <v-app>
    <v-container class="d-flex justify-center align-center main-container">
      <v-card elevation="10" class="app-card">

        <!-- HEADER -->
        <v-row>
          <v-col cols="12" class="text-center">
            <h1 class="rice-scan-title">RiceScan</h1>
          </v-col>
        </v-row>

        <!-- VIDEO STREAM -->
        <v-row justify="center" align="center" class="video-wrapper">
          <v-col cols="12" sm="10" class="d-flex justify-center">
            <div class="video-container">
              <video ref="video" autoplay playsinline v-show="videoStream" class="video-element"></video>
              <canvas ref="canvas" style="display: none;"></canvas>

              <!-- GRID -->
              <div v-if="gridEnabled" class="grid-overlay"></div>

              <!-- SKELETON LOADER -->
              <v-skeleton-loader
                v-if="loading"
                class="skeleton-loader"
                type="card"
                :loading="loading"
              ></v-skeleton-loader>

              <!-- SCAN PROGRESS LINE (NOT WORKING) -->
              <div v-if="isClassifying" class="scan-progress-line"></div>

              <!-- FLASH & GRID BUTTON -->
              <div class="toggle-buttons">
                <v-btn icon @click="toggleFlash" :class="{'active': flashOn}" class="flash-btn">
                  <v-icon>{{ flashOn ? 'mdi-flash-on' : 'mdi-flash' }}</v-icon>
                </v-btn>
                <v-btn icon @click="toggleGrid" :class="{'active': gridOn}" class="grid-btn">
                  <v-icon>{{ gridOn ? 'mdi-grid-large' : 'mdi-grid' }}</v-icon>
                </v-btn>
              </div>
            </div>
          </v-col>
        </v-row>

        <!-- SCAN, UPLOAD, AND CLASSIFY BUTTONS -->
        <v-row justify="center" align="center" class="mt-5 action-buttons">
          <v-col v-if="!scanStarted" cols="12" sm="6" md="4" class="d-flex justify-center">
            <v-btn @click="startScan" class="action-btn scan-btn">
              <v-icon left>mdi-camera</v-icon> Start Scan
            </v-btn>
          </v-col>

          <!-- UPLOAD AND CLASSIFY CONDITIONALS -->
          <v-col v-if="scanStarted" cols="12" sm="6" md="4" class="d-flex justify-center">
            <v-btn @click="triggerFileInput" class="action-btn upload-btn">
              <v-icon left>mdi-upload</v-icon> Upload Image
            </v-btn>
            <input
              type="file"
              ref="fileInput"
              accept="image/*"
              @change="handleFileUpload"
              style="display: none"
            />
          </v-col>

          <v-col v-if="scanStarted" cols="12" sm="6" md="4" class="d-flex justify-center">
            <v-btn @click="captureImage" class="action-btn classify-btn">
              <v-icon left>mdi-check-circle</v-icon> Classify Rice
            </v-btn>
          </v-col>
        </v-row>

        <!-- RESULT OR ERROR MESSAGE BELOW VIDEO STREAM WITH BOX BORDER -->
        <v-row v-if="resultMessage" justify="center" align="center" class="mt-5">
          <v-col cols="12" sm="6" class="d-flex justify-center">
            <v-card class="result-box" outlined>
              <v-card-title class="text-center">
                <v-icon large :color="isError ? 'red' : 'green'">
                  {{ isError ? 'mdi-alert-circle' : 'mdi-check-circle' }}
                </v-icon>
              </v-card-title>
              <v-card-text class="text-center">
                <p v-if="isClassifying">Scanning sample, please wait...</p>
                <p v-if="!isError">{{ riceType }}</p>
                <p v-if="isError">{{ resultMessage }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- CLOSE BUTTON TO RESET TO START SCAN -->
        <v-row v-if="resultMessage" justify="center" align="center" class="mt-3">
          <v-col cols="12" sm="6" class="d-flex justify-center">
            <v-btn @click="closeScan" color="secondary">Close</v-btn>
          </v-col>
        </v-row>

        <!-- FOOTER -->
        <v-row justify="center" class="mt-5">
          <v-col cols="12" class="text-center">
            <p>&copy; 2024 RiceScan</p>
          </v-col>
        </v-row>
      </v-card>
    </v-container>
  </v-app>
</template>

<!----- SCRIPTS ----->
<script>
import axios from 'axios';
import { VBtn, VIcon, VSkeletonLoader } from 'vuetify/components';

export default {
  name: 'App',
  components: {
    VBtn,
    VIcon,
    VSkeletonLoader,
  },
  data() {
    return {
      dialog: false,
      scanStarted: false,
      resultPopup: false,
      imageUploaded: false,
      resultMessage: '',
      isError: false,
      riceType: '',
      flashOn: false,
      gridOn: false,
      loading: false,
      isClassifying: false,
      showRetryButton: false,
      image: null,
      videoStream: null,
      isUploading: false,
    };
  },

  //=== METHODS ===//
  methods: {

    //=== FLASH BUTTON ===//
    toggleFlash() {
      this.flashOn = !this.flashOn;
    },

    //=== GRID BUTTON ===//
    toggleGrid() {
      this.gridOn = !this.gridOn;
      this.gridEnabled = this.gridOn;
    },

    //=== START SCANNING ===//
    startScan() {
      const video = this.$refs.video;
      if (!this.videoStream) {
        navigator.mediaDevices
          .getUserMedia({ video: true })
          .then((stream) => {
            video.srcObject = stream;
            this.videoStream = stream;
            this.scanStarted = true;
          })
          .catch((error) => {
            this.showError("Error accessing the camera.");
          });
      }
    },

    //=== CAPTURE USING CAMERA API ===//
    captureImage() {
      const canvas = this.$refs.canvas;
      const video = this.$refs.video;
      const context = canvas.getContext("2d");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const dataURL = canvas.toDataURL("image/jpeg");
      this.image = this.dataURLtoFile(dataURL, "captured-image.jpg");
      this.showRetryButton = true;
      this.classifyRice();
    },

    //=== HANDLES DATAURL ===//
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

    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    //=== FILE UPLOAD ===// 
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file && file.type.startsWith("image/")) {
        this.image = file;
        this.showRetryButton = true;
        this.classifyRice();
      } else {
        this.showError("Invalid file. Please upload a valid image.");
      }

      this.$refs.fileInput.value = null;
    },

    ///=== CLASSIFY RICE ===//
    async classifyRice() {
      this.isClassifying = true;
      this.loading = true;
      this.isError = false;

      const formData = new FormData();
      formData.append("image", this.image);

      try {
        const response = await axios.post('http://localhost:8000/api/classify/', formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        this.resultMessage = response.data.result;
        this.isError = false;
        this.riceType = response.data.riceType;
        this.resultPopup = true;
        this.loading = false;
      } catch (error) {
        this.showError("Failed to classify the rice. Please try again.");
      } finally {
        this.isClassifying = false;
        this.loading = false;
      }
    },

    //=== ERROR ===//
    showError(message) {
      this.resultMessage = message;
      this.isError = true;
      this.resultPopup = true;
    },

    //=== CLOSE BUTTON FUNCTION ===//
    closeScan() {
      this.resultPopup = false;
      this.isError = false;
      this.riceType = ''; 
      this.resultMessage = ''; 
      this.scanStarted = false;
      this.showRetryButton = false;

      if (this.videoStream) {
        this.videoStream.getTracks().forEach(track => track.stop());
        this.videoStream = null;
      }
      this.showStartScanButton = true; 
    },
  },
};
</script>

<style scoped>
/* Global Typography */
body {
  margin: 0;
  font-family: 'Poppins', sans-serif;
  background-color: #a8e6cf;
  color: #333;
  padding: 10px;
  box-sizing: border-box;
}

/* Main Container */
.main-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(180deg, #a8e6cf 0%, #dcedc1 100%);
  background-size: 200% 200%;
  animation: gradientAnimation 5s ease infinite;
  overflow: hidden;
  padding: 0 20px;
}

.main-container > .v-container {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border-radius: 20px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.9);
}

/* Card and title */
.app-card {
  padding: 20px;
  max-width: 600px;
  width: 100%;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
}

.rice-scan-title {
  color: #4caf50;
  font-weight: bold;
  font-size: 36px;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-family: 'Roboto', sans-serif;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.2);
  animation: heartbeat 1.5s ease-in-out infinite;
  transition: transform 0.3s ease, color 0.3s ease, text-shadow 0.3s ease;
}

.rice-scan-title:hover {
  transform: scale(1.1);
  color: #388e3c;
  text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.3);
}

.rice-scan-title:active {
  transform: scale(1.05);
  color: #2e7d32;
}

/* Video Container */
.video-container {
  position: relative;
  width: 100%;
  height: 350px;
  overflow: hidden;
  border: 2px solid #eee;
  border-radius: 12px;
  background-color: #000;
}

.video-element {
  width: 100%;
  height: 100%;
  border-radius: 10px;
  object-fit: cover;
}

/* Grid Overlay */
.grid-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.2) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(255, 255, 255, 0.2) 1px, transparent 1px);
  background-size: 20px 20px;
  opacity: 0.6;
  transition: opacity 0.2s ease-in-out;
}

.grid-overlay:hover {
  opacity: 0.8;
}

/* Skeleton Loader */
.skeleton-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 3;
}

/* Scan Line */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  height: 3px;
  width: 100%;
  background: rgba(0, 255, 0, 0.7);
  animation: scanAnimation 2s infinite;
  z-index: 10;
}

@keyframes scanAnimation {
  0% {
    top: 0;
  }
  100% {
    top: 100%;
  }
}

/* Buttons */
.action-btn {
  margin-bottom: 10px;
  background: linear-gradient(45deg, #4caf50, #81c784);
  color: #fff;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s;
}

.action-btn:hover {
  background: linear-gradient(45deg, #388e3c, #66bb6a);
  transform: scale(1.05);
}

/* Toggle Buttons */
.toggle-buttons {
  display: flex;
  gap: 10px;
  position: absolute;
  bottom: 10px;
  right: 10px;
  z-index: 4;
}

.flash-btn,
.grid-btn {
  background-color: rgba(255, 255, 255, 0.9);
  color: #000;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
}

.flash-btn:hover,
.grid-btn:hover {
  background-color: #4caf50;
  color: #fff;
}

.toggle-buttons .active {
  background-color: #4caf50;
  color: #fff;
}

/* Result Box */
.result-box {
  border: 2px solid #4caf50;
  border-radius: 10px;
  padding: 20px;
  background-color: #ffd54f;
}

.result-box .v-icon {
  margin-bottom: 10px;
}

.result-box p {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

/* Buttons */
.action-buttons {
  gap: 15px;
}

.scan-btn {
  background-color: #81c784;
  color: #fff;
}

.upload-btn {
  background-color: #ffd54f;
  color: #fff;
}

.classify-btn {
  background-color: #64b5f6;
  color: #fff;
}

.action-btn:hover {
  opacity: 0.9;
}

/* Result Card */
.result-card {
  padding: 20px;
  background-color: #e8f5e9;
  border-radius: 12px;
}

.headline {
  color: #388e3c;
  font-size: 18px;
}

.text-h6 {
  font-size: 16px;
  color: #333;
}

/* Responsiveness */
@media (max-width: 600px) {
  .video-container {
    height: 300px;
  }

  .video-element {
    border-radius: 5px;
  }

  .error-popup-card {
    padding: 20px;
    text-align: center;
    border-radius: 10px;
  }

  .error-popup-card p {
    margin: 10px 0;
    font-size: 14px;
  }
}

/* Gradient Animation */
@keyframes gradientAnimation {
  0% {
    background-position: 0% 0%;
  }
  50% {
    background-position: 100% 100%;
  }
  100% {
    background-position: 0% 0%;
  }
}

/* Heartbeat Animation */
@keyframes heartbeat {
  0%, 100% {
    transform: scale(1);
    color: #4caf50;
  }
  25% {
    transform: scale(1.2);
    color: #388e3c;
  }
  50% {
    transform: scale(1);
    color: #4caf50;
  }
  75% {
    transform: scale(1.2);
    color: #388e3c;
  }
}
</style>