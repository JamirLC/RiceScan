module.exports = {
  presets: [
    '@vue/cli-plugin-babel/preset',
  ],
  overrides: [
    {
      test: './node_modules/@mdi/js/mdi.js',
      compact: false,
    },
  ],
};
