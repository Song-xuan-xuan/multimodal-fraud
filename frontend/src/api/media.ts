export interface ProxyImageCandidate {
  src: string
  mode: 'proxy' | 'origin'
}

const DEFAULT_PROXY_PATH = '/api/v1/media/proxy-image'

function isHttpUrl(url: string) {
  return /^https?:\/\//i.test(url)
}

export const mediaApi = {
  buildCandidates(rawUrl: string): ProxyImageCandidate[] {
    const source = (rawUrl || '').trim()
    if (!source) {
      return []
    }

    if (!isHttpUrl(source)) {
      return [{ src: source, mode: 'origin' }]
    }

    const proxyPath = (import.meta.env.VITE_MEDIA_PROXY_PATH || DEFAULT_PROXY_PATH).trim() || DEFAULT_PROXY_PATH
    const encoded = encodeURIComponent(source)

    return [
      { src: `${proxyPath}?url=${encoded}`, mode: 'proxy' },
      { src: source, mode: 'origin' },
    ]
  },
}
