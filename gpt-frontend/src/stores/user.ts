import { ref } from 'vue'
import { defineStore } from 'pinia'
import { showNotify } from 'vant'
export const useUserStore = defineStore('user', () => {
    const token = ref('')
    const username = ref('游客')
    const avatar = ref('')
    const balance = ref(0)
    const chatSessions = ref<any[]>([])
    const currentSession = ref('')
    const prompts = ref<any[]>([])
    const textSending = ref(true)
    const currentPrompt = ref({ name: 'ChatGPT助手', promptId: -1 })
    type Chat = {
        role: string
        content: string
    }
    const currentChat = ref<Chat[]>([])
    async function login(code: String) {
        const res = await fetch(`/api/user/auth?code=${code}`)
        const data: any = await res.json()
        token.value = data.token
        username.value = data.username
        avatar.value = data.avatar
    }

    async function allChatSession() {
        const res = await fetch('/api/chat/all', {
            method: 'GET',
            headers: { Authorization: `Bearer ${token.value}` }
        })
        if (res.status == 200) {
            return await res.json()
        } else {
            return null
        }
    }

    async function newChat(promptid: number = -1) {
        const res = await fetch(`/api/chat/create?promptid=${promptid}`, {
            method: 'GET',
            headers: { Authorization: `Bearer ${token.value}` }
        })
        const sessionid: string = await res.text()
        currentChat.value = []
        return sessionid
    }

    async function getUserInfo() {
        const res = await fetch('/api/user/info', {
            method: 'GET',
            headers: { Authorization: `Bearer ${token.value}` }
        })
        const userInfo = await res.json()
        balance.value = userInfo.balance
        username.value = userInfo.username
        avatar.value = userInfo.avatar
        return userInfo
    }

    async function getChat(session_id: string) {
        const res = await fetch(`/api/chat/get?sessionid=${session_id}`, {
            method: 'GET',
            headers: { Authorization: `Bearer ${token.value}` }
        })
        const result = await res.json()
        currentChat.value = result.content
        if (result.prompt == null) {
            currentPrompt.value = { name: 'ChatGPT助手', promptId: -1 }
        } else {
            currentPrompt.value = { name: result.prompt.name, promptId: result.prompt.id }
        }
        return result.content
    }

    async function getAllPrompts() {
        const res = await fetch(`/api/prompt/all`, {
            method: 'GET',
            headers: { Authorization: `Bearer ${token.value}` }
        })
        const result = await res.json()
        prompts.value = result
        return result
    }

    async function* sendChat(content: string, session_id: string) {
        const res = await fetch('/api/chat/send', {
            method: 'POST',
            body: JSON.stringify({
                content: content,
                sessionid: session_id
            }),
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token.value}`
            }
        })
        if (res.status == 200) {
            const reader = res.body!.getReader()
            while (true) {
                const { value, done } = await reader.read()
                if (done) {
                    break // 读取完毕
                } else {
                    const chunk = new TextDecoder().decode(value)
                    currentChat.value[currentChat.value.length - 1].content += chunk
                    yield chunk
                }
            }
        } else {
            const error = await res.json()
            showNotify({ type: 'danger', message: error.detail.message })
            currentChat.value.pop()
            currentChat.value.pop()
        }
    }

    async function pay(premiumId: number) {
        const res = await fetch(`/api/pay/jsapi?premiumId=${premiumId}`, {
            method: 'GET',
            headers: { Authorization: `Bearer ${token.value}` }
        })

        return await res.json()
    }
    return {
        username,
        avatar,
        token,
        balance,
        currentChat,
        chatSessions,
        currentSession,
        prompts,
        currentPrompt,
        textSending,
        getAllPrompts,
        login,
        allChatSession,
        newChat,
        getChat,
        sendChat,
        getUserInfo,
        pay
    }
})
