<template>
    <van-row>
        <van-image round :src="userStore.avatar" width="6rem" height="6rem" />
        <van-col class="user-info">
            <div class="name">{{ userStore.username }}</div>
            <van-row class="balance">
                <van-space>
                    <van-icon name="underway-o" />
                    <div>余额：{{ userStore.balance }}</div>
                </van-space>
            </van-row>
        </van-col>
    </van-row>
</template>
<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { onMounted } from 'vue';
const userStore = useUserStore();

onMounted(() => {
    userStore.getUserInfo();
});

</script>

<style scoped>
.user-info {
    display: flex;
    flex-direction: column;
    justify-content: center;
    /* 将元素在交叉轴上居中对齐 */
    align-items: start;
    /* 将元素在主轴上居中对齐 */
    margin-left: 24px;
}

.name {
    font-size: 1.5rem;
    font-weight: bold;
}

.balance {
    font-size: 1rem;
}
</style>