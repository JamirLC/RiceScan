import { createApp } from 'vue';
import App from './App.vue';
import './registerServiceWorker';
import router from './router';
import vuetify from './plugins/vuetify';
import '@mdi/font/css/materialdesignicons.css';

const app = createApp(App);

// Set the global API URL accessible throughout the app
app.config.globalProperties.$apiUrl = "http://127.0.0.1:8000"; // Django backend API

app
  .use(router)
  .use(vuetify)
  .mount('#app');
