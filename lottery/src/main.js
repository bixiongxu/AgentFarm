import { createApp } from 'vue'
import App from './App.vue'
import ViewUIPlus from 'view-ui-plus'
import router from './router'
import 'view-ui-plus/dist/styles/viewuiplus.css'

import axios from "axios";

const app = createApp(App)

app
  .use(router)
  .use(ViewUIPlus)
  .mount('#app')