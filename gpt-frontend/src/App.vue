<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

</script>

<template>
  <!-- 开启顶部安全区适配 -->
  <!-- <van-nav-bar safe-area-inset-top /> -->
  <van-col class="main">
    <suspense>
      <RouterView />
    </suspense>
  </van-col>
  <navigation-bar />
  <!-- 开启底部安全区适配 -->
  <van-number-keyboard safe-area-inset-bottom />
</template>

<style scoped>
.main {
  margin-bottom: 175px;
}

/* 
@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
} */
</style>
