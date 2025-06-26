import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '../views/Register.vue'
import LandingPage from '@/views/LandingPage.vue'
import StudyTopics from '@/views/StudyTopics.vue'
import StudyHistory from '@/views/StudyHistory.vue'
import StudyTimer from '@/views/StudyTimer.vue'
import Timetable from '@/views/Timetable.vue'
import Notifications from '@/views/Notifications.vue'
import AccountInformation from '@/views/AccountInformation.vue'
import AdminUserList from '@/views/AdminUserList.vue'
import AdminStats from '@/views/AdminStats.vue'
import AdminReminder from '@/views/AdminReminder.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import UserStats from '@/views/UserStats.vue'
import AddTopic from '@/views/AddTopic.vue'
import Clock from '@/views/Clock.vue'


const routes = [
    {
      path: '/',
      name: 'landingpage',
      component: LandingPage,
    },
    {
      path: '/login',
      name: 'login',
      component: Login ,
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
    },
    {
      path: '/home',
      name: 'home',
      component: Home,
    },
    {
      path: '/topics',
      name: 'topics',
      component: StudyTopics,
    },
    {
      path: '/history',
      name: 'history',
      component: StudyHistory,
    },
    {
      path: '/timer',
      name: 'timer',
      component: StudyTimer,
    },
    {
      path: '/timetable',
      name: 'timetable',
      component: Timetable,
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: Notifications,
    },
    {
      path: '/accountinformation',
      name: 'accountinformation',
      component: AccountInformation,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
    },
    {
      path: '/adminuserlist',
      name: 'adminuserlist',
      component: AdminUserList,
    },
    {
      path: '/adminstats',
      name: 'adminstats',
      component: AdminStats,
    },
    {
      path: '/adminreminders',
      name: 'adminreminders',
      component: AdminReminder,
    },
    {
      path: '/userstats',
      name: 'userstats',
      component: UserStats,
    },
    {
      path: '/addtopic',
      name: 'addtopic',
      component: AddTopic,
    },
        {
      path: '/clock',
      name: 'clock',
      component: Clock,
    },
  ];

// Tạo instance của Vue Router
const router = createRouter({
  history: createWebHistory(), 
  routes // Định nghĩa các routers
})

export default router