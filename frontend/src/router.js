import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import AboutView from './views/AboutView.vue'
import UsersView from './views/UsersView.vue'
import RequestIndex from './views/Request/Index.vue'
import RequestCreate from './views/Request/Create.vue'
import RequestEdit from './views/Request/Edit.vue'
import RequestView from './views/Request/View.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView
  },
  {
    path: '/users',
    name: 'users',
    component: UsersView
  },
  {
    path: '/requests',
    name: 'requests',
    component: RequestIndex
  },
  {
    path: '/requests/create',
    name: 'requests-create',
    component: RequestCreate
  },
  {
    path: '/requests/:id/edit',
    name: 'requests-edit',
    component: RequestEdit,
    props: true
  }
  ,
  {
    path: '/requests/:id',
    name: 'requests-view',
    component: RequestView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router