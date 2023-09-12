<template>
    <van-col>
        <van-row class="namerow">
            <van-icon :name=props.avatar size="1.5rem" />
            <div class="name">{{ props.name }} :</div>
        </van-row>
        <div :class="{ gptcontent: props.role == 'gpt', content: true }">
            <MdPreview :editorId='id' :modelValue="computeMessage" />
        </div>
    </van-col>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';
import { computed } from 'vue';

const props = defineProps({
    avatar: { type: String, default: '/gpt_avatar.svg' },
    name: String,
    message: String,
    role: {
        type: String,
        validator: (value: string) => {
            return ['user', 'gpt'].includes(value);
        }
    }
})
const id = "preview-only"
const computeMessage = computed(() => {
    if (props.message == "") {
        return "..."
    }
    return props.message;
})

</script>

<style scoped>
.content {
    width: 100%;
    height: 100%;
    overflow: auto;
    border-radius: 6px;
}

.gptcontent {
    background-color: #f5f5f5;
}

.md-editor {
    --md-bk-color: #00000000;
}

.name {
    margin-left: 12px;
    font-size: large;
    font-weight: bolder;
}

.namerow {
    margin: 8px;
    align-items: center;
}
</style>
