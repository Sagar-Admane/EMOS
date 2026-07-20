export const getApiUrl = (path) => {
  const apiBase = import.meta.env.VITE_API_URL;
  if (apiBase) {
    const base = apiBase.endsWith('/') ? apiBase.slice(0, -1) : apiBase;
    return `${base}${path.replace(/^\/api/, '')}`;
  }
  return path;
};
