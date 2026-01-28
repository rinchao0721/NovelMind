/**
 * LLM Provider 配置
 * 参考 Cherry Studio 的实现
 */

// 导入图标
import openaiLogo from '@/assets/images/providers/openai.png'
import anthropicLogo from '@/assets/images/providers/anthropic.png'
import geminiLogo from '@/assets/images/providers/gemini.png'
import deepseekLogo from '@/assets/images/providers/deepseek.png'
import dashscopeLogo from '@/assets/images/providers/dashscope.png'
import zhipuLogo from '@/assets/images/providers/zhipu.png'
import baiduLogo from '@/assets/images/providers/baidu-cloud.svg'
import aihubmixLogo from '@/assets/images/providers/aihubmix.png'
import siliconLogo from '@/assets/images/providers/silicon.png'
import openrouterLogo from '@/assets/images/providers/openrouter.png'
import ollamaLogo from '@/assets/images/providers/ollama.png'
import customLogo from '@/assets/images/providers/custom.svg'

/**
 * Provider 配置接口
 */
export interface ProviderConfig {
  /** 唯一标识 */
  id: string
  /** 显示名称 */
  name: string
  /** Logo 图片路径 */
  logo: string
  /** 备用 Emoji (用于图片加载失败时) */
  emoji: string
  /** API Base URL */
  defaultBaseUrl?: string
  /** 官网链接 */
  website?: string
  /** 是否需要 API Key */
  requiresApiKey: boolean
  /** 是否需要 Secret Key (如百度) */
  requiresSecretKey?: boolean
  /** 是否支持自定义 Base URL */
  supportsCustomBaseUrl: boolean
  /** 默认模型列表 */
  defaultModels: string[]
}

/**
 * Provider Logo 映射表
 */
export const PROVIDER_LOGO_MAP: Record<string, string> = {
  openai: openaiLogo,
  claude: anthropicLogo,
  gemini: geminiLogo,
  deepseek: deepseekLogo,
  qwen: dashscopeLogo,
  zhipu: zhipuLogo,
  baidu: baiduLogo,
  aihubmix: aihubmixLogo,
  siliconflow: siliconLogo,
  openrouter: openrouterLogo,
  ollama: ollamaLogo,
  custom: customLogo,
}

/**
 * Provider Emoji 映射表 (备用)
 */
export const PROVIDER_EMOJI_MAP: Record<string, string> = {
  openai: '🤖',
  claude: '🧠',
  gemini: '✨',
  deepseek: '🐋',
  qwen: '☁️',
  zhipu: '🚀',
  baidu: '🐼',
  aihubmix: '🔄',
  siliconflow: '⚡',
  openrouter: '🌐',
  ollama: '🦙',
  custom: '⚙️',
}

/**
 * 所有支持的 Provider 配置
 */
export const PROVIDERS: ProviderConfig[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    logo: openaiLogo,
    emoji: '🤖',
    defaultBaseUrl: 'https://api.openai.com/v1',
    website: 'https://platform.openai.com',
    requiresApiKey: true,
    supportsCustomBaseUrl: true,
    defaultModels: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  },
  {
    id: 'claude',
    name: 'Claude',
    logo: anthropicLogo,
    emoji: '🧠',
    defaultBaseUrl: 'https://api.anthropic.com',
    website: 'https://console.anthropic.com',
    requiresApiKey: true,
    supportsCustomBaseUrl: false,
    defaultModels: ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229'],
  },
  {
    id: 'gemini',
    name: 'Gemini',
    logo: geminiLogo,
    emoji: '✨',
    defaultBaseUrl: 'https://generativelanguage.googleapis.com',
    website: 'https://ai.google.dev',
    requiresApiKey: true,
    supportsCustomBaseUrl: false,
    defaultModels: ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],
  },
  {
    id: 'deepseek',
    name: 'DeepSeek',
    logo: deepseekLogo,
    emoji: '🐋',
    defaultBaseUrl: 'https://api.deepseek.com',
    website: 'https://platform.deepseek.com',
    requiresApiKey: true,
    supportsCustomBaseUrl: false,
    defaultModels: ['deepseek-chat', 'deepseek-reasoner'],
  },
  {
    id: 'qwen',
    name: '阿里百炼',
    logo: dashscopeLogo,
    emoji: '☁️',
    defaultBaseUrl: 'https://dashscope.aliyuncs.com/api/v1',
    website: 'https://dashscope.console.aliyun.com',
    requiresApiKey: true,
    supportsCustomBaseUrl: false,
    defaultModels: ['qwen-max', 'qwen-plus', 'qwen-turbo'],
  },
  {
    id: 'zhipu',
    name: '智谱 AI',
    logo: zhipuLogo,
    emoji: '🚀',
    defaultBaseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    website: 'https://open.bigmodel.cn',
    requiresApiKey: true,
    supportsCustomBaseUrl: false,
    defaultModels: ['glm-4', 'glm-4-flash', 'glm-3-turbo'],
  },
  {
    id: 'baidu',
    name: '百度文心',
    logo: baiduLogo,
    emoji: '🐼',
    defaultBaseUrl: 'https://aip.baidubce.com',
    website: 'https://cloud.baidu.com/product/wenxinworkshop',
    requiresApiKey: true,
    requiresSecretKey: true,
    supportsCustomBaseUrl: false,
    defaultModels: ['ernie-4.0-8k', 'ernie-3.5-8k', 'ernie-speed'],
  },
  {
    id: 'aihubmix',
    name: 'AIHubMix',
    logo: aihubmixLogo,
    emoji: '🔄',
    defaultBaseUrl: 'https://aihubmix.com/v1',
    website: 'https://aihubmix.com',
    requiresApiKey: true,
    supportsCustomBaseUrl: true,
    defaultModels: ['gpt-4o', 'claude-3-5-sonnet-20241022', 'gemini-1.5-pro-latest'],
  },
  {
    id: 'siliconflow',
    name: '硅基流动',
    logo: siliconLogo,
    emoji: '⚡',
    defaultBaseUrl: 'https://api.siliconflow.cn/v1',
    website: 'https://siliconflow.cn',
    requiresApiKey: true,
    supportsCustomBaseUrl: true,
    defaultModels: ['deepseek-ai/DeepSeek-V3', 'deepseek-ai/DeepSeek-R1', 'Qwen/Qwen2.5-72B-Instruct'],
  },
  {
    id: 'openrouter',
    name: 'OpenRouter',
    logo: openrouterLogo,
    emoji: '🌐',
    defaultBaseUrl: 'https://openrouter.ai/api/v1',
    website: 'https://openrouter.ai',
    requiresApiKey: true,
    supportsCustomBaseUrl: true,
    defaultModels: ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet', 'google/gemini-pro-1.5'],
  },
  {
    id: 'ollama',
    name: 'Ollama',
    logo: ollamaLogo,
    emoji: '🦙',
    defaultBaseUrl: 'http://localhost:11434/v1',
    website: 'https://ollama.com',
    requiresApiKey: false,
    supportsCustomBaseUrl: true,
    defaultModels: ['llama3', 'mistral', 'qwen2'],
  },
  {
    id: 'custom',
    name: '自定义 API',
    logo: customLogo,
    emoji: '⚙️',
    requiresApiKey: true,
    supportsCustomBaseUrl: true,
    defaultModels: [],
  },
]

/**
 * 根据 ID 获取 Provider 配置
 */
export function getProviderById(id: string): ProviderConfig | undefined {
  return PROVIDERS.find((p) => p.id === id)
}

/**
 * 根据 ID 获取 Provider Logo
 */
export function getProviderLogo(id: string): string {
  return PROVIDER_LOGO_MAP[id] || customLogo
}

/**
 * 根据 ID 获取 Provider Emoji
 */
export function getProviderEmoji(id: string): string {
  return PROVIDER_EMOJI_MAP[id] || '🤖'
}

/**
 * 根据 ID 获取 Provider 名称
 */
export function getProviderName(id: string): string {
  const provider = getProviderById(id)
  return provider?.name || id
}
