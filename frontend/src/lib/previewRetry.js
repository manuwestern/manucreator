// Only for read-only, non-billable rendering and asset loading. Never mutations.
export const withPreviewRetry = async operation => {
  for (let attempt = 0; ; attempt++) {
    try { return await operation(); }
    catch (error) {
      const transient = error.status !== undefined
        ? [408, 500, 502, 503, 504].includes(error.status)
        : error.name === 'NetworkError' || error.name === 'TypeError' || /network|fetch|load failed|verbindung|bild konnte.*geladen|service unavailable|bad gateway|gateway timeout|overload/i.test(error.message);
      if (!transient || attempt >= 2) throw error;
      await new Promise(resolve => setTimeout(resolve, 400 * (attempt + 1)));
    }
  }
};