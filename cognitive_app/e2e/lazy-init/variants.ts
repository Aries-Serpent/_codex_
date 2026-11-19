export const variants = {
  default: { api: undefined, timing: undefined, stageMs: 800 },
  noKey: { api: undefined, timing: undefined, stageMs: 800 },
  fast: { api: 'http://127.0.0.1:58001', timing: '200', stageMs: 200 },
  slow: { api: 'https://api.example.invalid', timing: '2000', stageMs: 2000 },
  zero: { api: undefined, timing: '0', stageMs: 800 },
  negative: { api: undefined, timing: '-500', stageMs: 800 },
  excessive: { api: undefined, timing: '20000', stageMs: 800 },
  invalid: { api: undefined, timing: 'invalid', stageMs: 800 },
  nan: { api: undefined, timing: 'NaN', stageMs: 800 },
  customAPI: { api: 'http://custom-api.invalid:3000/v1', timing: undefined, stageMs: 800 },
} as const;

export type Variant = keyof typeof variants;
export const variantNames = Object.keys(variants) as Variant[];

export function variantURL(name: Variant, firstPort: number, base: string) {
  return `http://localhost:${firstPort + variantNames.indexOf(name)}${base}`;
}
