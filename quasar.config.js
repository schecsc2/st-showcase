import { configure } from 'quasar/wrappers'

export default configure(() => ({
  boot: [
    'leaflet'
  ],

  css: [
    'app.scss'
  ],

  extras: [
    'material-icons'
  ],

  build: {
    vueRouterMode: 'hash'
  },

  devServer: {
    open: false
  },

  framework: {
    config: {},
    plugins: []
  },

  animations: []
}))
