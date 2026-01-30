<template>
  <el-tag :type="statusType" :size="size" :effect="effect">
    {{ statusText }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getStatusType, getStatusText } from '@/utils/status'

const props = withDefaults(defineProps<{
  status: string | undefined
  size?: 'large' | 'default' | 'small'
  effect?: 'dark' | 'light' | 'plain'
}>(), {
  size: 'small',
  effect: 'light'
})

const statusType = computed(() => getStatusType(props.status))
const statusText = computed(() => getStatusText(props.status))
</script>
