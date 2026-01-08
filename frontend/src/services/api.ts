import { Startup } from '@/types/risk';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function fetchStartups(): Promise<Startup[]> {
  const res = await fetch(`${API_BASE}/api/startups`);
  return handleResponse<Startup[]>(res);
}

export async function fetchStartup(id: string): Promise<Startup> {
  const res = await fetch(`${API_BASE}/api/startups/${id}`);
  return handleResponse<Startup>(res);
}
