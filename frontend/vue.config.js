const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  devServer: {
    https: {
      key: './key.pem',
      cert: './cert.pem',
    },
    port: 8080, // Optional: Change the port if needed
  },
};

