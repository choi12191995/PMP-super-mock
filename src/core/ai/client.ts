export interface AiConfig {
  baseURL: string
  apiKey: string
  model: string
  temperature: number
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

const REDACTED = '[REDACTED]'

function redactKey(text: string, apiKey: string): string {
  if (!apiKey) return text
  return text.split(apiKey).join(REDACTED)
}

function normalizeBaseURL(baseURL: string): string {
  return baseURL.replace(/\/+$/, '')
}

function buildHeaders(apiKey: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${apiKey}`,
  }
}

function parseErrorMessage(status: number, body: string, apiKey: string): string {
  let message = body
  try {
    const parsed = JSON.parse(body) as { error?: { message?: string } }
    if (parsed.error?.message) message = parsed.error.message
  } catch {
    /* use raw body */
  }

  message = redactKey(message, apiKey)

  if (status === 401) return 'Unauthorized — check your API key'
  if (status === 429) return 'Rate limited — try again later'
  if (status >= 500) return `Server error (${status})`
  return message || `Request failed (${status})`
}

async function postChat(
  config: AiConfig,
  messages: ChatMessage[],
  stream: boolean,
  signal?: AbortSignal,
): Promise<Response> {
  const url = `${normalizeBaseURL(config.baseURL)}/chat/completions`
  return fetch(url, {
    method: 'POST',
    headers: buildHeaders(config.apiKey),
    body: JSON.stringify({
      model: config.model,
      messages,
      temperature: config.temperature,
      stream,
    }),
    signal,
  })
}

export async function* streamChat(
  config: AiConfig,
  messages: ChatMessage[],
  signal?: AbortSignal,
): AsyncGenerator<string> {
  let response: Response
  try {
    response = await postChat(config, messages, true, signal)
  } catch (err) {
    if (signal?.aborted) return
    throw new Error(err instanceof Error ? err.message : 'Network error')
  }

  if (!response.ok) {
    const body = await response.text().catch(() => '')
    throw new Error(parseErrorMessage(response.status, body, config.apiKey))
  }

  if (!response.body) {
    throw new Error('No response body')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue

        const data = trimmed.slice(5).trim()
        if (data === '[DONE]') return

        try {
          const parsed = JSON.parse(data) as {
            choices?: { delta?: { content?: string } }[]
          }
          const chunk = parsed.choices?.[0]?.delta?.content
          if (chunk) yield chunk
        } catch {
          /* skip malformed SSE chunks */
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

export async function chat(
  config: AiConfig,
  messages: ChatMessage[],
  signal?: AbortSignal,
): Promise<string> {
  let response: Response
  try {
    response = await postChat(config, messages, false, signal)
  } catch (err) {
    if (signal?.aborted) throw new Error('Aborted')
    throw new Error(err instanceof Error ? err.message : 'Network error')
  }

  if (!response.ok) {
    const body = await response.text().catch(() => '')
    throw new Error(parseErrorMessage(response.status, body, config.apiKey))
  }

  const parsed = (await response.json()) as {
    choices?: { message?: { content?: string } }[]
  }
  return parsed.choices?.[0]?.message?.content?.trim() ?? ''
}

export async function testConnection(
  config: AiConfig,
): Promise<{ ok: boolean; error?: string }> {
  if (!config.baseURL.trim() || !config.apiKey.trim()) {
    return { ok: false, error: 'Endpoint and API key are required' }
  }

  try {
    const result = await chat(config, [{ role: 'user', content: 'Hi' }])
    if (!result) return { ok: false, error: 'Empty response from model' }
    return { ok: true }
  } catch (err) {
    return {
      ok: false,
      error: err instanceof Error ? err.message : 'Connection failed',
    }
  }
}

export async function fetchModels(baseURL: string, apiKey: string): Promise<string[]> {
  const url = `${normalizeBaseURL(baseURL)}/models`
  let response: Response
  try {
    response = await fetch(url, { headers: buildHeaders(apiKey) })
  } catch (err) {
    throw new Error(err instanceof Error ? err.message : 'Network error')
  }

  if (!response.ok) {
    const body = await response.text().catch(() => '')
    throw new Error(parseErrorMessage(response.status, body, apiKey))
  }

  const parsed = (await response.json()) as { data?: { id: string }[] }
  return (parsed.data ?? []).map((m) => m.id).sort()
}
