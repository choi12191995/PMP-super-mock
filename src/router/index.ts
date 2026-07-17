import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/mode',
    name: 'mode-picker',
    component: () => import('@/views/ModePickerView.vue'),
  },
  {
    path: '/exam',
    name: 'exam-room',
    component: () => import('@/views/ExamRoomView.vue'),
  },
  {
    path: '/results/:attemptId',
    name: 'results',
    component: () => import('@/views/ResultsView.vue'),
  },
  {
    path: '/review/:attemptId',
    name: 'review',
    component: () => import('@/views/ReviewView.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/HistoryView.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
