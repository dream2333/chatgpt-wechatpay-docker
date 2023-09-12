<template>
    <van-tabbar v-model="active" route>
        <!-- <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item> -->
        <van-tabbar-item icon="chat-o" to="/chat">对话</van-tabbar-item>
        <van-tabbar-item icon="friends-o" to="/user">我的</van-tabbar-item>
    </van-tabbar>
</template>
<script setup lang="ts">
import { ref } from 'vue';
const active = ref(1);

</script>