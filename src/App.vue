<template>
  <div class="app-container" :class="{ 'is-dark': isDark }">
    <el-config-provider :locale="zhCn">
      <!-- 侧边栏导航 -->
      <aside class="app-sidebar">
        <div class="logo">
          <h1>NovelMind</h1>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" active-class="active">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </router-link>
          <router-link to="/analysis" class="nav-item" active-class="active">
            <el-icon><DataAnalysis /></el-icon>
            <span>剧情分析</span>
          </router-link>
          <router-link to="/graph" class="nav-item" active-class="active">
            <el-icon><Share /></el-icon>
            <span>关系图谱</span>
          </router-link>
          <router-link to="/timeline" class="nav-item" active-class="active">
            <el-icon><Timer /></el-icon>
            <span>时间线</span>
          </router-link>
          <router-link to="/characters" class="nav-item" active-class="active">
            <el-icon><User /></el-icon>
            <span>人物列表</span>
          </router-link>
          <router-link to="/settings" class="nav-item" active-class="active">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </router-link>
        </nav>
        <div class="nav-footer">
          <button class="theme-toggle" @click="toggleDark">
            <el-icon><Moon v-if="!isDark" /><Sunny v-else /></el-icon>
          </button>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>

        <!-- 💡 后端加载遮罩 -->
        <transition name="fade">
          <div v-if="!isBackendReady" class="backend-loading-overlay">
            <el-icon class="is-loading"><Loading /></el-icon>
            <p>正在启动分析引擎...</p>
            <p class="retry-hint" v-if="loadingTime > 5000">正在进行首次初始化，请稍候</p>
          </div>
        </transition>
      </main>
    </el-config-provider>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { checkApiConnection } from '@/api'
import { Loading } from '@element-plus/icons-vue'

const isDark = ref(false)
const isBackendReady = ref(false)
const loadingTime = ref(0)
let checkInterval: any = null
let timerInterval: any = null

const toggleDark = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const startBackendCheck = () => {
  const startTime = Date.now()
  timerInterval = setInterval(() => {
    loadingTime.value = Date.now() - startTime
  }, 1000)

  checkInterval = setInterval(async () => {
    const connected = await checkApiConnection()
    if (connected) {
      isBackendReady.value = true
      clearInterval(checkInterval)
      clearInterval(timerInterval)
    }
  }, 1000)
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }

  startBackendCheck()
})

onUnmounted(() => {
  if (checkInterval) clearInterval(checkInterval)
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style lang="scss" scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
}

.backend-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(var(--bg-color-rgb), 0.9);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  color: var(--text-color);

  .el-icon {
    font-size: 48px;
    color: var(--primary-color);
    margin-bottom: 16px;
  }

  p {
    font-size: 16px;
    font-weight: 500;
  }

  .retry-hint {
    margin-top: 12px;
    font-size: 12px;
    color: var(--text-color-secondary);
  }
}

.app-sidebar {
  width: 220px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 16px 0;

  .logo {
    padding: 0 20px 20px;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 16px;

    h1 {
      font-size: 22px;
      font-weight: 700;
      color: var(--primary-color);
      margin: 0;
    }
  }

  .nav-menu {
    flex: 1;
    padding: 0 12px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    margin-bottom: 4px;
    border-radius: 8px;
    color: var(--text-color-secondary);
    text-decoration: none;
    transition: all 0.2s;

    &:hover {
      background: var(--hover-bg);
      color: var(--text-color);
    }

    &.active {
      background: var(--primary-color);
      color: #fff;
    }

    .el-icon {
      font-size: 18px;
    }

    span {
      font-size: 14px;
    }
  }

  .nav-footer {
    padding: 12px;
    border-top: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 8px;

    .nav-item {
      flex: 1;
      margin-bottom: 0;
    }

    .theme-toggle {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      border: none;
      background: var(--hover-bg);
      color: var(--text-color);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;

      &:hover {
        background: var(--primary-color);
        color: #fff;
      }

      .el-icon {
        font-size: 18px;
      }
    }
  }
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
