const SENSITIVE_KEYS = new Set(["card", "password", "pwd", "pass", "token", "authorization"]);

function sanitize(value) {
  if (!value || typeof value !== "object") {
    return value;
  }

  if (Array.isArray(value)) {
    return value.map(sanitize);
  }

  const sanitized = {};
  for (const [key, entry] of Object.entries(value)) {
    sanitized[key] = SENSITIVE_KEYS.has(key.toLowerCase()) ? "****" : sanitize(entry);
  }
  return sanitized;
}

function write(level, message, meta) {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
  };
  if (meta) {
    entry.meta = sanitize(meta);
  }
  const output = JSON.stringify(entry);
  if (level === "error") {
    console.error(output);
  } else {
    console.log(output);
  }
}

module.exports = {
  info: (message, meta) => write("info", message, meta),
  warn: (message, meta) => write("warn", message, meta),
  error: (message, meta) => write("error", message, meta),
};
