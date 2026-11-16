export const syntheticKey = 'synthetic-browser-key';
export const dashboardAPI = 'http://127.0.0.1:58002';

export const variants = {
  default: { key: syntheticKey, api: undefined, timing: undefined, stageMs: 800 },
  noKey: { key: '', api: undefined, timing: undefined, stageMs: 800 },
  fast: { key: syntheticKey, api: 'http://127.0.0.1:58001', timing: '200', stageMs: 200 },
  slow: { key: syntheticKey, api: 'https://api.example.invalid', timing: '2000', stageMs: 2000 },
  zero: { key: syntheticKey, api: undefined, timing: '0', stageMs: 800 },
  negative: { key: syntheticKey, api: undefined, timing: '-500', stageMs: 800 },
  excessive: { key: syntheticKey, api: undefined, timing: '20000', stageMs: 800 },
  invalid: { key: syntheticKey, api: undefined, timing: 'invalid', stageMs: 800 },
  nan: { key: syntheticKey, api: undefined, timing: 'NaN', stageMs: 800 },
  customAPI: { key: syntheticKey, api: 'http://custom-api.invalid:3000/v1', timing: undefined, stageMs: 800 },
} as const;

export type Variant = keyof typeof variants;
export const variantNames = Object.keys(variants) as Variant[];

export function variantURL(name: Variant, firstPort: number, base: string) {
  return `http://127.0.0.1:${firstPort + variantNames.indexOf(name)}${base}`;
}
