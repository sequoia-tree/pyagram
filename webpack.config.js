const path = require('path');

module.exports = {
  mode: 'production',
  entry: {
    main: [
      './src/scripts/init.js',
      './src/scripts/index.js',
    ],
  },
  output: {
    path: path.resolve('./static/scripts'),
    publicPath: '/static/scripts/',
    filename: '[name].js',
  },
};
