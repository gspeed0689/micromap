const path = require('path');

module.exports = {
  entry: './src/typescript/pollenbase.ts',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, './dist'),
    //libraryTarget: 'var',
    library: 'PollenBase'
  },
  resolve:{
    extensions: [".ts", ".js"]
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: ["ts-loader"],
      }
    ],
  },
  mode: "development"
}