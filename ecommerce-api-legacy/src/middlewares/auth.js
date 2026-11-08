const crypto = require("crypto");

const { AppError } = require("../utils/errors");

function createRequireAdmin(config) {
  return (req, res, next) => {
    if (!config.adminToken) {
      return next();
    }

    const provided = req.get("X-Admin-Token") || "";
    const expected = config.adminToken;
    const valid =
      provided.length === expected.length &&
      crypto.timingSafeEqual(Buffer.from(provided), Buffer.from(expected));

    if (!valid) {
      return next(new AppError("Não autorizado", 401));
    }

    return next();
  };
}

module.exports = { createRequireAdmin };
