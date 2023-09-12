import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import ChatView from '@/views/ChatView.vue'
import UserView from '@/views/UserView.vue'
import { useUserStore } from '@/stores/user'
import pinia from '@/stores/store'


const userStore = useUserStore(pinia)
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            // 访问根路径重定向到/home
            path: '/',
            redirect: '/chat'
        },
        {
            path: '/home',
            name: 'home',
            component: HomeView
        },
        {
            path: '/chat',
            name: 'chat',
            component: ChatView
        },
        {
            path: '/user',
            name: 'user',
            component: UserView
        }
    ]
})

router.beforeResolve(async (to, from) => {
  console.log(window.location.href)
  if (!userStore.token && !to.query.code) {
    // 如果未登录将用户重定向到登录页面
    const appid = 'wx9e2803a81b64be1d'
    const callbackUrl = window.location.href
    const redirectUrl = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appid}&redirect_uri=${callbackUrl}&response_type=code&scope=snsapi_userinfo&state=0#wechat_redirect&forcePopup=true`
    window.location.href = redirectUrl
  } else if (!userStore.token && to.query.code) {
    // 跳转回来的时候，进行登录
    await userStore.login(to.query.code.toString())
    return { path: to.path }
  }
})

export default router
