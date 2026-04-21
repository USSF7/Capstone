import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import 'flowbite'
import App from './App.vue'
import router from './router'

/**
 * Create Vue application instance
 */
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
