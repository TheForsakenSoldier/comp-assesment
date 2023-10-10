const path = require('path');

module.exports = {
  entry: './src/javascript/masterpage.jsx',
  output: {
    filename: 'master-page.js',
    path: path.resolve(__dirname, './static'),
    publicPath: '/static/',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/, // Add this rule to handle CSS files
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  module: {
    rules: [
      {
        test: /\.(png|jpe?g|gif)$/i,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'images/', // Specify the output path for the images
              publicPath: 'images/', // Specify the public URL path for the images
            },
          },
        ],
      },
    ],
  },
  resolve: {
    extensions: ['.png', '.jpeg', '.gif', ],
  },
};
