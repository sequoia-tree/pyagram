const path = require('path');

module.exports = {
  mode: 'production',
  entry: {
    main: [
      './src/scripts/editor.js',
      './src/scripts/decode.js',
    ],
  },
  output: {
    path: path.resolve('./static/scripts'),
    publicPath: '/static/scripts/',
    filename: '[name].js',
  },
};
