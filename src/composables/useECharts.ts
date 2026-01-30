import { ref, onMounted, onUnmounted, nextTick, type Ref } from 'vue'
import * as echarts from 'echarts'

export interface UseEChartsOptions {
  autoResize?: boolean
  watchVisibility?: boolean
}

export function useECharts(
  chartRef: Ref<HTMLElement | undefined>, 
  theme?: string | object,
  options: UseEChartsOptions = {}
) {
  let chart: echarts.ECharts | null = null
  let resizeObserver: ResizeObserver | null = null
  let intersectionObserver: IntersectionObserver | null = null
  const isVisible = ref(true)
  const isReady = ref(false)

  /**
   * 检查容器是否有有效尺寸
   */
  const hasValidSize = (el: HTMLElement): boolean => {
    const rect = el.getBoundingClientRect()
    const hasSize = rect.width > 0 && rect.height > 0
    
    if (!hasSize) {
      console.warn('[ECharts] Container has no valid size:', {
        width: rect.width,
        height: rect.height,
        clientWidth: el.clientWidth,
        clientHeight: el.clientHeight
      })
    }
    
    return hasSize
  }

  /**
   * 等待容器获得有效尺寸
   */
  const waitForValidSize = async (el: HTMLElement, maxWait = 3000): Promise<boolean> => {
    const startTime = Date.now()
    let attempts = 0
    
    while (!hasValidSize(el)) {
      attempts++
      const elapsed = Date.now() - startTime
      
      if (elapsed > maxWait) {
        console.error('[ECharts] Timeout waiting for valid container size after', attempts, 'attempts')
        return false
      }
      
      // 等待更长时间让 DOM 和 CSS 渲染
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    
    console.log('[ECharts] Container ready after', attempts, 'attempts')
    return true
  }

  /**
   * 初始化图表
   */
  const initChart = async (): Promise<echarts.ECharts | null> => {
    if (!chartRef.value) {
      console.warn('[ECharts] Cannot init: chartRef is undefined')
      return null
    }
    
    // 等待 DOM 更新
    await nextTick()
    
    // 等待容器有有效尺寸
    const hasSize = await waitForValidSize(chartRef.value)
    if (!hasSize) {
      console.error('[ECharts] Failed to initialize: container has no valid size')
      return null
    }
    
    // 销毁旧实例
    if (chart) {
      console.log('[ECharts] Disposing old chart instance')
      chart.dispose()
      chart = null
    }
    
    try {
      // 初始化新实例
      chart = echarts.init(chartRef.value, theme)
      isReady.value = true
      console.log('[ECharts] Chart initialized successfully', {
        width: chartRef.value.clientWidth,
        height: chartRef.value.clientHeight
      })
      return chart
    } catch (error) {
      console.error('[ECharts] Failed to initialize chart:', error)
      isReady.value = false
      return null
    }
  }

  /**
   * 调整图表大小
   */
  const resize = () => {
    if (!chart || !chartRef.value) {
      return
    }
    
    if (!hasValidSize(chartRef.value)) {
      console.warn('[ECharts] Cannot resize: container has no valid size')
      return
    }
    
    try {
      chart.resize({
        width: 'auto',
        height: 'auto'
      })
      console.log('[ECharts] Chart resized:', {
        width: chartRef.value.clientWidth,
        height: chartRef.value.clientHeight
      })
    } catch (error) {
      console.error('[ECharts] Failed to resize:', error)
    }
  }

  /**
   * 设置图表选项
   */
  const setOption = async (option: echarts.EChartsOption, notMerge: boolean = true) => {
    // 确保图表已初始化
    if (!chart) {
      console.log('[ECharts] Chart not initialized, initializing now...')
      await initChart()
    }
    
    if (!chart) {
      console.error('[ECharts] Cannot set option: chart initialization failed')
      return
    }
    
    // 等待 DOM 更新
    await nextTick()
    
    // 验证容器尺寸
    if (chartRef.value && !hasValidSize(chartRef.value)) {
      console.warn('[ECharts] Setting option on hidden or zero-size container')
    }
    
    try {
      chart.setOption(option, notMerge)
      console.log('[ECharts] Option set successfully')
    } catch (error) {
      console.error('[ECharts] Failed to set option:', error)
    }
  }

  /**
   * 获取图表实例
   */
  const getInstance = (): echarts.ECharts | null => chart

  // 生命周期钩子
  onMounted(() => {
    console.log('[ECharts] Component mounted')
    
    // 监听窗口 resize
    window.addEventListener('resize', resize)
    
    // 使用 ResizeObserver 监听容器尺寸变化（如果支持且启用）
    if (options.autoResize && chartRef.value && typeof ResizeObserver !== 'undefined') {
      console.log('[ECharts] Setting up ResizeObserver')
      resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          console.log('[ECharts] Container resized:', {
            width: entry.contentRect.width,
            height: entry.contentRect.height
          })
          resize()
        }
      })
      resizeObserver.observe(chartRef.value)
    }
    
    // 使用 IntersectionObserver 监听可见性（如果支持且启用）
    if (options.watchVisibility && chartRef.value && typeof IntersectionObserver !== 'undefined') {
      console.log('[ECharts] Setting up IntersectionObserver')
      intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const wasVisible = isVisible.value
          isVisible.value = entry.isIntersecting
          
          console.log('[ECharts] Visibility changed:', {
            from: wasVisible,
            to: isVisible.value
          })
          
          // 从隐藏变为可见时，调整大小
          if (!wasVisible && isVisible.value) {
            nextTick(() => {
              console.log('[ECharts] Container became visible, resizing...')
              resize()
            })
          }
        })
      }, {
        threshold: 0.1 // 至少 10% 可见时触发
      })
      intersectionObserver.observe(chartRef.value)
    }
    
    // 监听标签页可见性变化
    const handleVisibilityChange = () => {
      if (!document.hidden && chart) {
        console.log('[ECharts] Tab became visible, resizing...')
        nextTick(() => resize())
      }
    }
    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    // 监听 CSS 过渡结束
    const handleTransitionEnd = () => {
      console.log('[ECharts] Transition ended, resizing...')
      resize()
    }
    chartRef.value?.addEventListener('transitionend', handleTransitionEnd)
    
    // 清理函数
    onUnmounted(() => {
      console.log('[ECharts] Component unmounted, cleaning up...')
      window.removeEventListener('resize', resize)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      chartRef.value?.removeEventListener('transitionend', handleTransitionEnd)
      resizeObserver?.disconnect()
      intersectionObserver?.disconnect()
      chart?.dispose()
      chart = null
      isReady.value = false
    })
  })

  return {
    initChart,
    setOption,
    resize,
    getInstance,
    isVisible,
    isReady
  }
}
