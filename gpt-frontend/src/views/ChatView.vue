

<template>
  <van-col>
    <template v-for="item, index in userStore.currentChat" :key="index">
      <chat-box v-if="item.role == 'user'" :name="userStore.username" :message="item.content" role="user"
        :avatar="userStore.avatar"></chat-box>
      <chat-box v-else :name="userStore.currentPrompt.name" :message="item.content" role="gpt"></chat-box>
    </template>
    <!-- 列表底部元素，用于滚动视图使用 -->
    <div ref="chatContentRef" />
  </van-col>
  <van-cell-group inset class="chat-input">
    <van-row class="van-hairline--top" style="padding: 10px 10px 0px 10px;">
      <van-space size="8px">
        <van-button :disabled="userStore.textSending" plain hairline round size="small" icon="replay"
          style="padding: 0px 10px 0px 10px;" text="刷新" @click="() => refresh()" />
        <van-button :disabled="userStore.textSending" plain hairline round size="small" icon="smile-o"
          style="padding: 0px 10px 0px 10px;" text="角色" @click="showChar = true" />
        <van-button :disabled="userStore.textSending" plain hairline round size="small" icon="delete-o"
          style="padding: 0px 10px 0px 10px;" text="清空" @click="() => newChat(userStore.currentPrompt.promptId)" />
      </van-space>
    </van-row>
    <van-field v-model="input_text" rows="3" type="textarea" maxlength="10000" placeholder="请输入对话内容" show-word-limit>
      <template #button>
        <van-button size="small" :disabled="userStore.textSending" :loading="userStore.textSending" type="primary"
          @click="sendChat">发送</van-button>
      </template>
    </van-field>
    <van-popup :show="showChar" round position="bottom">
      <van-picker :columns="userStore.prompts" @cancel="showChar = false" @confirm="onConfirm" />
    </van-popup>
  </van-cell-group>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { nextTick } from 'vue';
import { showNotify, showConfirmDialog } from 'vant';
import 'vant/es/notify/style'

// 获取底部元素
const chatContentRef = ref<HTMLElement>()
const userStore = useUserStore();
const input_text = ref('')
const showChar = ref(false)

userStore.textSending = true

function onConfirm(selectedItem: any) {
  showConfirmDialog({
    title: '更换GPT当前的角色',
    message:
      '将ChatGPT更换为当前选中角色会清空当前对话，是否继续？',
  }).then(async () => {
    const promptid = selectedItem.selectedOptions[0].value
    const name = selectedItem.selectedOptions[0].text
    userStore.currentPrompt = { name: name, promptId: promptid }
    await userStore.newChat(promptid)
    userStore.chatSessions = await userStore.allChatSession()
    userStore.currentSession = userStore.chatSessions[0].session_id
    userStore.currentChat = []
    showChar.value = false
    showNotify({
      type: 'success',
      message: '更换成功',
    })
  }).catch(() => { });

}
if (!userStore.token) {
  throw new Error('请先登录');
}
// 滚动到底部
function scrollToBottom(behavior: ScrollBehavior = 'smooth') {
  chatContentRef.value?.scrollIntoView({ behavior: behavior })
}
onMounted(async () => {
  if (userStore.currentSession.length == 0) {
    // 获取最新的chatSessionId
    userStore.chatSessions = await userStore.allChatSession()
    // 如果还没有聊天记录，则创建一个
    if (!userStore.chatSessions) {
      userStore.currentSession = await userStore.newChat()
    }
    else {
      userStore.currentSession = userStore.chatSessions[0].session_id
      await userStore.getChat(userStore.currentSession)
    }
    // 获取prompts
    const prompts = await userStore.getAllPrompts()
    userStore.prompts = prompts.map((item: any) => {
      return { text: item.name, value: item.id }
    })
    userStore.prompts.splice(0, 0, { text: "ChatGPT助手", value: -1 })
    scrollToBottom()
  }
  else {
    scrollToBottom('instant')
  }
  userStore.textSending = false
});


// 发送对话后追加到聊天记录
async function sendChat() {
  userStore.textSending = true
  const userText = input_text.value.toString().trim()
  if (!userText) {
    showNotify('内容不能为空');
    userStore.textSending = false
    return
  }
  userStore.currentChat.push({
    role: 'user',
    content: userText
  })
  userStore.currentChat.push({
    role: 'assistant',
    content: ''
  })
  input_text.value = ''
  await nextTick()
  scrollToBottom()
  const chat = await userStore.sendChat(userText, userStore.currentSession)
  // eslint-disable-next-line no-constant-condition
  for await (let chunk of chat) {
    await nextTick()
    scrollToBottom()
  }
  userStore.textSending = false
}

async function newChat(promptid: number = -1) {
  if (userStore.currentChat.length > 0) {
    await userStore.newChat(promptid)
    userStore.chatSessions = await userStore.allChatSession()
    userStore.currentSession = userStore.chatSessions[0].session_id
    userStore.currentChat = []
  }
  else {
    showNotify('对话为空，无需清除');
  }
}

async function refresh() {
  await userStore.getChat(userStore.currentSession)
  scrollToBottom()
  showNotify({
    type: 'success',
    message: '刷新成功',
  });
}


</script>

<style scoped>
.chat-input {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  margin-bottom: 50px;
}
</style>
