import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../views/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/Login.vue')
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('../views/auth/ForgotPassword.vue')
    },
    {
      path: '/reset-password', 
      name: 'reset-password',
      component: () => import('../views/auth/ResetPassword.vue') 
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/Register.vue')
    },
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('../views/management/Dashboard.vue') 
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/management/Dashboard.vue')
        },
        {
          path: 'change-password',
          name: 'change-password',
          component: () => import('../views/auth/ChangePassword.vue')
        },
        {
          path: 'users',
          children: [
            {
              path: 'teacher',
              name: 'users-teacher',
              component: () => import('../views/management/UsersTeacher.vue')
            },
            {
              path: 'student',
              name: 'users-student',
              component: () => import('../views/management/UsersStudent.vue')
            }
          ]
        },
        {
          path: 'chemicals',
          component: () => import('../views/management/Chemicals.vue'), 
          children: [
            {
        path: 'encyclopedia',
        name: 'chemicals-encyclopedia',
        component: () => import('../views/management/ChemicalsEncyclopedia.vue')
      },

            {
              path: 'warehouse',
              name: 'chemicals-warehouse',
              component: () => import('../views/management/ChemicalsWarehouse.vue') 
            },
            
          ]
        },
        {
          path: 'purchase',
          component: () => import('../views/application/Purchase.vue'), 
          children: [
            {
              path: 'application',
              name: 'purchase-application',
              component: () => import('../views/application/PurchaseApplication.vue')
            },
            {
              path: 'inbound',
              name: 'purchase-inbound',
              component: () => import('../views/application/PurchaseInbound.vue')
            }
          ]
        },
        {
          path: 'borrow',
          component: () => import('../views/application/Borrow.vue'), 
          children: [
            {
              path: 'application',
              name: 'borrow-application',
              component: () => import('../views/application/BorrowApplication.vue')
            },
            {
              path: 'outbound',
              name: 'borrow-outbound',
              component: () => import('../views/application/BorrowOutbound.vue')
            }
          ]
        },
        {
          path: 'scrap',
          component: () => import('../views/application/Scrap.vue'), 
          children: [
            {
              path: 'application',
              name: 'scrap-application',
              component: () => import('../views/application/ScrapApplication.vue')
            },
            {
              path: 'outbound',
              name: 'scrap-outbound',
              component: () => import('../views/application/ScrapOutbound.vue')
            }
          ]
        },
        {
          path: 'allocation',
          component: () => import('../views/application/Allocation.vue'),
          children: [
            {
              path: 'application',
              name: 'allocation-application',
              component: () => import('../views/application/AllocationApplication.vue')
            },
            {
              path: 'inbound',
              name: 'allocation-inbound',
              component: () => import('../views/application/AllocationInbound.vue')
            }
          ]
        }
      ]
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  const publicPages = ['/login', '/forgot-password', '/register','/reset-password'];
  const authRequired = !publicPages.includes(to.path);
  const authStore = useAuthStore();

  // Ensure auth state is loaded before proceeding
  await authStore.verifyTokenOnLoad();

  const loggedIn = authStore.isAuthenticated;

  // trying to access a restricted page + not logged in
  if (authRequired && !loggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router
