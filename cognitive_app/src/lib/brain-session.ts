const sessionPromises = new Map<string, Promise<boolean>>();

export async function ensureBrainSession(baseURL: string): Promise<boolean> {
  const normalized = baseURL.replace(/\/$/, '');
  const pending = sessionPromises.get(normalized);
  if (pending) return pending;

  const request = fetch(`${normalized}/api/session`, {
    method: 'POST',
    credentials: 'include',
  }).then(response => response.ok).catch(() => false);

  sessionPromises.set(normalized, request);
  const established = await request;
  if (!established) sessionPromises.delete(normalized);
  return established;
}
