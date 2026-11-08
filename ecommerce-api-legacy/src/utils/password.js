const crypto = require("crypto");

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(String(password), salt, 64).toString("hex");
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  if (typeof stored !== "string") {
    return false;
  }

  if (!stored.includes(":")) {
    return stored === String(password);
  }

  const [salt, expectedHex] = stored.split(":");
  if (!salt || !expectedHex) {
    return false;
  }

  const expected = Buffer.from(expectedHex, "hex");
  const candidate = crypto.scryptSync(String(password), salt, 64);
  return expected.length === candidate.length && crypto.timingSafeEqual(expected, candidate);
}

module.exports = { hashPassword, verifyPassword };
