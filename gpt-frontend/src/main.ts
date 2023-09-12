import './assets/main.css'
import 'md-editor-v3/lib/preview.css'
import { createApp } from 'vue'
import pinia from './stores/store'
import App from './App.vue'
import router from './router'
import 'vant/lib/index.css'

const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app')
