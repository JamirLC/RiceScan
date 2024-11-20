<template>
  <v-app>
    <v-container>
      <!-- Header Section -->
      <v-row>
        <v-col cols="12" class="text-center">
          <svg-icon :type="'mdi'" :path="mdiRice" large></svg-icon>
          <h1 class="rice-scan-title">RiceScan</h1>
        </v-col>
      </v-row>

      <!-- Video Stream Section -->
      <v-row justify="center" align="center" class="mb-4">
        <v-col cols="12" sm="8" md="6" class="d-flex justify-center video-container">
          <video ref="video" autoplay playsinline v-show="videoStream" class="video-element"></video>
          <canvas ref="canvas" style="display: none;"></canvas>

          <v-skeleton-loader v-if="loading" class="skeleton-loader" type="card"></v-skeleton-loader>
        </v-col>
      </v-row>

      <!-- Start Scan Button -->
      <v-row justify="center" class="mt-5">
        <v-col cols="12" sm="6" md="4">
          <v-btn @click="startScan" color="primary" block class="small-btn rounded-btn">
            Start the Scan
          </v-btn>
        </v-col>
      </v-row>

      <!-- Upload Image Button Section -->
      <v-row justify="center" class="mt-5">
        <v-col cols="12" sm="6" md="4">
          <v-btn @click="triggerFileInput" color="secondary" block class="small-btn rounded-btn">
            Upload an Image
          </v-btn>
          <input type="file" ref="fileInput" accept="image/*" @change="handleFileUpload" style="display: none" />
        </v-col>
      </v-row>

      <!-- Prediction Result Section -->
      <v-row justify="center" class="mt-4">
        <v-col cols="12" sm="6" md="4">
          <v-card elevation="10" class="result-card">
            <v-card-actions class="d-flex justify-center">
              <v-btn @click="classifyRice" color="primary" class="small-btn rounded-btn" large>Classify Rice</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <!-- Error Message Section -->
      <v-row v-if="errorMessage" justify="center" class="mt-4">
        <v-col cols="12" sm="6" md="4">
          <v-alert type="error" dismissible>{{ errorMessage }}</v-alert>
        </v-col>
      </v-row>


      <!-- Footer -->
      <v-row justify="center" class="mt-5">
        <v-col cols="12" class="text-center">
          <p>&copy; 2024 RiceScan</p>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import axios from 'axios';
import { mdiRice } from '@mdi/js';
import { VBtn, VIcon, VSkeletonLoader } from 'vuetify/components';
import SvgIcon from '@jamescoyle/vue-icon';

export default {
  name: 'App',
  components: {
    VBtn,
    VIcon,
    VSkeletonLoader,
    SvgIcon,
  },
  data() {
    return {
      resultMessage: "Rice type will be displayed here.",
      videoStream: null,
      image: null,
      predictionStatus: '',
      errorMessage: null,
      loading: false,
      mdiRice,
      gridEnabled: true,
    };
  },
  methods: {
    toggleFlash() {
      console.log("Flash toggled!");
    },
    toggleGrid() {
      this.gridEnabled = !this.gridEnabled;
    },
    startScan() {
      const video = this.$refs.video;
      if (!this.videoStream) {
        navigator.mediaDevices
          .getUserMedia({ video: true })
          .then((stream) => {
            video.srcObject = stream;
            this.videoStream = stream;
          })
          .catch((error) => {
            this.errorMessage = "Error accessing the camera.";
          });
      }
    },
    captureImage() {
      const canvas = this.$refs.canvas;
      const video = this.$refs.video;
      const context = canvas.getContext("2d");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const dataURL = canvas.toDataURL("image/jpeg");
      this.image = this.dataURLtoFile(dataURL, "captured-image.jpg");
      this.classifyRice();
    },
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
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file && file.type.startsWith("image/")) {
        this.image = file;
        this.classifyRice();
      } else {
        this.errorMessage = "Please upload a valid image.";
      }
    },
    
    async classifyRice() {
      this.loading = true;
      const formData = new FormData();
      formData.append("image", this.image);

      try {
        const response = await axios.post(this.$apiUrl, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        this.resultMessage = response.data.result;
        this.predictionStatus = 'success';
      } catch (error) {
        console.error("Error:", error);
        this.errorMessage = "Failed to classify the rice. Please try again.";
        this.predictionStatus = 'error';
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
/* Global Styles */
body {
  margin: 0;
  font-family: 'Arial', sans-serif;
  background-color: #a8e6cf;
  color: #333;
  padding: 10px;
  box-sizing: border-box;
}

.rice-scan-title {
  font-family: 'Poppins', sans-serif;  /* Use a clean, modern font */
  font-size: 3rem;                     /* Larger font size */
  font-weight: bold;                   /* Bold text */
  color: #4caf50;                      /* Green color for a fresh look */
  letter-spacing: 2px;                 /* Slightly spaced letters */
  text-transform: uppercase;           /* Uppercase letters for emphasis */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); /* Subtle shadow to make text pop */
  transition: transform 0.3s ease-in-out; /* Smooth hover effect */
}

/* Hover effect for title */
.rice-scan-title:hover {
  transform: scale(1.1);               /* Slight scale-up effect on hover */
  color: #388e3c;                      /* Darker green on hover */
}

.video-container {
  display: flex;
  justify-content: center; 
  align-items: center;     
  width: 100%;            
  max-width: 600px;       
  height: 450px;           
  margin: 0 auto;          
  border: 6px solid #4caf50;  
  border-radius: 12px;     
  box-sizing: border-box;  
  padding: 0;              
}

/* Video Element Styling */
.video-element {
  width: 100%;           
  height: 100%;          
  border-radius: 10px;   
  object-fit: cover;     
}

/* Skeleton Loader */
.skeleton-loader {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 600px;
  height: 300px;
  background-color: #ccc;
  border-radius: 10px;
  z-index: 9999;
}

.small-btn {
  font-size: 12px;         /* Smaller font size for compact appearance */
  padding: 6px 12px;       /* Reduced padding for a smaller button */
  height: 32px;            /* Smaller height for the button */
  line-height: 32px;       /* Centers the text vertically */
  border-radius: 4px;      /* Rounded corners */
  background-color: #4caf50; /* Button color */
  color: white;            /* Text color */
  border: none;            /* No border */
  cursor: pointer;         /* Pointer cursor on hover */
  transition: background-color 0.3s ease; /* Smooth background change on hover */
  min-width: 120px;        /* Set a minimum width for the button */
  margin: 0 auto;          /* Center the button horizontally */
}

.small-btn:hover {
  background-color: #388e3c; /* Darker green on hover */
}

.rounded-btn {
  border-radius: 50px;
}

/* Result Card */
.result-card {
  padding: 20px;
  background-color: #e8f5e9;
}

.headline {
  color: #388e3c;
}

.text-h6 {
  font-size: 18px;
  color: #333;
}

.result-card .v-btn {
  margin-top: 10px;
}

/* Responsive Adjustments */
@media (max-width: 600px) {
  .video-container {
    height: 300px;         /* Reduce height on small screens */
  }

  .video-element {
    border-radius: 5px;    /* Slightly smaller rounded corners on mobile */
  }
}
</style>
