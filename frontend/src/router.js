/**
 * The different routes in the application that help organize the different views.
 * @module Router
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'
import HomeView from './views/Home/Index.vue'
import CreateProfileView from './views/Profile/Create.vue'
import EditProfileView from './views/Profile/Edit.vue'
import ViewProfileView from './views/Profile/View.vue'
import EarningsProfileView from './views/Profile/Earnings.vue'
import LoginView from './views/Auth/login.vue'
import LogoutView from './views/Auth/logout.vue'
import CallbackView from './views/Auth/callback.vue'
import RentalIndex from './views/Rental/Index.vue'
import RentalView from './views/Rental/View.vue'

/**
 * Application route definitions.
 * Each route maps a URL path to a Vue component view.
 */
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
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
    path: '/profile/view/:id',
    name: 'view_profile',
    component: ViewProfileView
  },
  {
    path: '/profile/earnings',
    name: 'earnings_profile',
    component: EarningsProfileView
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
    path: '/equipment/:id/view',
    name: 'equipment-view',
    component: () => import('./views/Inventory/View.vue'),
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
  {
    path: '/equipment/search',
    name: 'equipment-search',
    component: () => import('./views/Equipment/Search.vue'),
  },
  {
    path: '/rentals',
    name: 'rentals',
    component: RentalIndex
  },
  {
    path: '/rentals/create',
    name: 'rental_create',
    component: () => import('./views/Rental/Create.vue')
  },
  {
    path: '/rentals/view/:id',
    name: 'rental_view',
    component: RentalView
  },
  {
    path: '/rentals/:id/edit',
    name: 'rental-edit',
    component: () => import('./views/Rental/Edit.vue'),
  },
  {
    path: '/rentals/:id/meeting',
    name: 'rental-meeting',
    component: () => import('./views/Rental/MeetingLocation.vue'),
  }
]

/**
 * Vue Router instance
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

/**
 * Routes that do NOT require authentication
 */
const publicPages = ['login', 'logout', 'auth-callback', 'home', 'about']

router.beforeEach((to) => {
  const auth = useAuthStore()

  // Allow public pages without auth
  if (publicPages.includes(to.name)) {
    return
  }

  // Redirect to login if not authenticated
  if (!auth.isAuthenticated) {
    return { name: 'login' }
  }

  // If authenticated but profile incomplete, redirect to complete profile
  if (!auth.profileComplete && to.name !== 'create_profile') {
    return { name: 'create_profile' }
  }
})

export default router
