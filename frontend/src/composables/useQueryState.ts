import type { LocationQuery, LocationQueryRaw, Router } from 'vue-router'

export function asString(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim() ? value : undefined
}

export function asPositiveInt(value: unknown, fallback: number, min = 1, max = Number.MAX_SAFE_INTEGER): number {
  const n = Number(value)
  if (!Number.isInteger(n) || n <= 0) return fallback
  return Math.min(Math.max(n, min), max)
}

function normalizeQueryValue(value: unknown): string[] {
  if (value === undefined) return []
  if (Array.isArray(value)) return value.map((v) => String(v))
  return [String(value)]
}

function isSameQuery(current: LocationQuery, next: LocationQueryRaw): boolean {
  const currentKeys = Object.keys(current).filter((k) => current[k] !== undefined)
  const nextKeys = Object.keys(next).filter((k) => next[k] !== undefined)

  if (currentKeys.length !== nextKeys.length) return false

  const keySet = new Set([...currentKeys, ...nextKeys])
  for (const key of keySet) {
    const a = normalizeQueryValue(current[key])
    const b = normalizeQueryValue(next[key])
    if (a.length !== b.length) return false
    for (let i = 0; i < a.length; i += 1) {
      if (a[i] !== b[i]) return false
    }
  }
  return true
}

export async function replaceQueryKeepingOthers(
  router: Router,
  routeQuery: LocationQuery,
  removeKeys: string[],
  nextEntries: Record<string, string>,
): Promise<boolean> {
  const query: LocationQueryRaw = { ...routeQuery }
  for (const key of removeKeys) delete query[key]

  const nextQuery: LocationQueryRaw = {
    ...query,
    ...nextEntries,
  }

  if (isSameQuery(routeQuery, nextQuery)) return false
  await router.replace({ query: nextQuery })
  return true
}
