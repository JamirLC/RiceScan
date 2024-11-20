import { createApp } from 'vue';
import App from './App.vue';
import './registerServiceWorker';
import router from './router';
import vuetify from './plugins/vuetify';

const app = createApp(App);

// Global API URL
app.config.globalProperties.$apiUrl = "http://localhost:8000";

app
  .use(router)
  .use(vuetify)
  .mount('#app');
