<template>
    <van-col>
        <user-info-bar class="user-info-card" />
        <van-button type="primary" block :onClick="() => showList = true">购买次数</van-button>
    </van-col>
    <van-popup class="popup" v-model:show="showList" round position="bottom">
        <van-col>
            <!-- <van-row>
                <premium-card :price="10" :balance="30" @click="purchase(0)" text="体验会员包"/>
            </van-row> -->
            <van-row>
                <premium-card :price="10" :balance="100" @click="purchase(0)" text="中级会员包"/>
            </van-row>
            <van-row>
                <premium-card :price="30" :balance="500" @click="purchase(1)" text="高级会员包" />
            </van-row>
            <!-- <van-row>
                <premium-card :price="100" :balance="1000" @click="purchase(3)" text="高级会员包"/>
            </van-row> -->
        </van-col>
    </van-popup>
</template>
<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { showNotify } from 'vant';
import { ref } from 'vue';
import wx from 'weixin-js-sdk-ts'

const userStore = useUserStore();
const showList = ref(false);

async function purchase(premiumId: number) {
    const result = (await userStore.pay(premiumId)).result;
    console.log(result);
    wx.config({
        debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
        appId: result.appId, // 必填，公众号的唯一标识
        timestamp: result.timestamp, // 必填，生成签名的时间戳
        nonceStr: result.nonceStr, // 必填，生成签名的随机串
        signature: result.signature, // 必填，签名
        jsApiList: ["chooseWXPay"],// 必填，需要使用的JS接口列表
        openTagList: []
    })
    wx.ready(() => {
        wx.chooseWXPay({
            timestamp: result.timeStamp,
            nonceStr: result.nonceStr,
            package: result.package,
            signType: result.signType,
            paySign: result.paySign,
            success: (res: any) => {
                // 支付成功时返回resolve
                console.log(res);
                showNotify({
                    type: 'success',
                    message: '支付成功',
                });
                showList.value = false;
            },
            fail: (err: any) => {
                // 支付失败时返回reject
                console.log(err);
                showNotify({
                    type: 'danger',
                    message: '支付失败，请在手机端微信浏览器内进行操作，如已成功请联系管理员',
                });
            },
            cancel: (err: any) => {
                // 支付失败时返回reject
                console.log(err);
                showNotify({
                    type: 'warning',
                    message: '支付取消',
                });
            }
        })
    })
}

</script>

<style>
.user-info-card {
    margin-bottom: 24px;
}

.price {
    font-size: 1.5rem;
    font-weight: bold;
    color: rgb(203, 42, 42);
}

.van-coupon__valid {
    visibility: hidden;
}

.popup {
    padding: 36px 20px 36px 20px;
    height: '80%';
    background: #f4f4f7;
}
</style>