import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import AboutView from './views/AboutView.vue'
import UsersView from './views/UsersView.vue'
import CreateProfileView from './views/Profile/Create.vue'
import EditProfileView from './views/Profile/Edit.vue'
import ViewProfileView from './views/Profile/View.vue'
import EarningsProfileView from './views/Profile/Earnings.vue'
import EventIndex from './views/Event/Index.vue'
import EventCreate from './views/Event/Create.vue'
import EventEdit from './views/Event/Edit.vue'
import EventView from './views/Event/View.vue'
import InventoryView from './views/Profile/Inventory.vue'
import RequestIndex from './views/Request/Index.vue'
import RequestCreate from './views/Request/Create.vue'
import RequestEdit from './views/Request/Edit.vue'
import RequestView from './views/Request/View.vue'
import LoginView from './views/Auth/login.vue'
import LogoutView from './views/Auth/logout.vue'
import CallbackView from './views/Auth/callback.vue'
import RecommendationsView from './views/Profile/Recommendations.vue'

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
  },
  {
    path: '/profile/edit',
    name: 'edit_profile',
    component: EditProfileView
  },
  {
    path: '/profile/view',
    name: 'view_profile',
    component: ViewProfileView
  },
  {
    path: '/profile/earnings',
    name: 'earnings_profile',
    component: EarningsProfileView
  },
  {
    path: '/inventory',
    name: 'inventory',
    component: InventoryView
  },
  {
    path: '/events',
    name: 'events',
    component: EventIndex
  },
  {
    path: '/events/create',
    name: 'events-create',
    component: EventCreate
  },
  {
    path: '/events/:id/edit',
    name: 'events-edit',
    component: EventEdit,
    props: true
  },
  {
    path: '/events/:id',
    name: 'events-view',
    component: EventView,
    props: true
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
  },
  {
    path: '/requests/:id',
    name: 'requests-view',
    component: RequestView,
    props: true
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/logout',
    name: 'logout',
    component: LogoutView
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: CallbackView
  },
  {
    path: '/recommendations',
    name: 'recommendations',
    component: RecommendationsView
  },
  {
    path: '/equipment',
    name: 'inventory',
    component: () => import('./views/Inventory/Index.vue')
  },
  {
    path: '/equipment/:id/edit',
    name: 'equipment-edit',
    component: () => import('./views/Inventory/Edit.vue'),
    props: true
  },
  {
    path: '/equipment/create',
    name: 'equipment-create',
    component: () => import('./views/Inventory/Create.vue')
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: () => import('./views/Profile/Calendar.vue')
  },
  // {
  //   path: '/rentals/:id',
  //   name: 'rentals-view',
  //   component: () => import('./views/Rental/View.vue'),
  //   props: true
  // }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
