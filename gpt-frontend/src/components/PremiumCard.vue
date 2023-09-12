<template>
    <div class="rounded van-haptics-feedback">
        <van-row>
            <van-col align="center">
                <van-row justify="center" align="center">
                    <div :style="{ 'font-size': 'x-large', 'font-weight': 'bolder', 'color': '#36ace1' }">{{ props.price }}
                    </div>
                    <div :style="{ 'font-weight': 'bolder', 'color': '#36ace1' }">元</div>
                </van-row>
                {{ props.text }}
            </van-col>
            <van-row align="center" justify="center">
                <div :style="{ 'margin-left': '40px' }">
                    {{ props.balance }}次对话次数
                </div>
            </van-row>
        </van-row>
    </div>
</template>
<script setup lang="ts">
const props = defineProps({
    price: {
        type: Number,
        required: true
    },
    balance: {
        type: Number,
        required: true
    },
    text: {
        type: String,
        required: true
    }
})
</script>
<style>
.rounded {
    margin: 8px 16px 8px 16px;
    border-radius: 6px;
    padding: 16px;
    background-color: #ffffff;
    width: 100%;
    box-shadow: 0 0 6px 1px #e5e7ea;
}
</style>