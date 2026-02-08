/** @type {(api: any) => void} */
export default function register(api) {
  // Minimal runtime plugin: exposes metadata only.
  // Core council execution is file-based via SKILL + council.py.
  api.logger?.info?.('[openclaw-council] plugin loaded');
}
