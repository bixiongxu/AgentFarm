import { createRouter, createWebHistory } from 'vue-router'
import Root from "@/views/Root.vue";
import Recommend from "@/views/Recommend.vue"
import History from "@/views/History.vue"
import Liuyao from "@/views/Liuyao.vue"
import ContentFilter from "@/views/ContentFilter.vue"
import Stock from "@/views/Stock.vue"
import AgentFeed from "@/views/AgentFeed.vue"
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Root",
      components: {
        root: Root
      },
      children: [{
          path: "/recommend",
          name: "Recommend",
          component: Recommend,
        },{
          path: "/history",
          name: "History",
          component: History,
        },{
          path: "/bagua",
          name: "Liuyao",
          component: Liuyao,
        },{
          path: "/cf",
          name: "ContentFilter",
          component: ContentFilter,
        },{
          path: "/stock",
          name: "Stock",
          component: Stock,
        },{
          path: "/agentfeed",
          name: "AgentFeed",
          component: AgentFeed,
        },
      ]
    }]
})

export default router
