import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
    plugins: [vue()],
    server: {
        https: {
            key: './192.168.199.160-key.pem',
            cert: './192.168.199.160.pem',
        },
        host: true, // Binds to all available network interfaces, including localhost
        port: 8080, // You can specify any port you'd like
    },
});
