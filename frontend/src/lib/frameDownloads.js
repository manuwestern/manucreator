// One shared queue also bounds overlapping loader lifetimes (toggle/resize).
// Target prioritization happens in heroFrames; no path bypasses this hard cap.
const queue = [];
let active = 0;
const MAX_DOWNLOADS = 2;

const drain = () => {
  while (active < MAX_DOWNLOADS && queue.length) {
    const job = queue.shift();
    if (job.signal.aborted) {
      job.reject(new DOMException('Download cancelled', 'AbortError'));
      continue;
    }
    active += 1;
    fetch(job.url, { signal: job.signal })
      .then(response => {
        if (!response.ok) throw new Error('Frame sheet unavailable');
        return response.blob();
      })
      .then(job.resolve, job.reject)
      .finally(() => {
        // Release only after the entire body is consumed and the browser has
        // completed the network lifecycle, not when response headers arrive.
        setTimeout(() => { active -= 1; drain(); }, 0);
      });
  }
};

export const downloadFrameSheet = (url, signal) => new Promise((resolve, reject) => {
  queue.push({ url, signal, resolve, reject });
  drain();
});