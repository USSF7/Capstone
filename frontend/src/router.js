import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import AboutView from './views/AboutView.vue'
import UsersView from './views/UsersView.vue'
import CreateProfileView from './views/Profile/Create.vue'

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
    path: '/profile/create',
    name: 'create_profile',
    component: CreateProfileView
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router