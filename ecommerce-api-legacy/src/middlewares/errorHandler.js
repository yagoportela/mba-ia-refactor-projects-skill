const logger = require("../utils/logger");

function notFoundHandler(req, res) {
  res.status(404).json({ error: "Rota não encontrada" });
}

function errorHandler(error, req, res, next) {
  let status = error.status || 500;
  if (error.type === "entity.parse.failed") {
    status = 400;
  }

  if (status >= 500) {
    logger.error("Erro não tratado", {
      method: req.method,
      path: req.path,
      error: error.message,
    });
  }

  res.status(status).json({
    error: status >= 500 ? "Erro interno" : error.message,
  });
}

module.exports = { notFoundHandler, errorHandler };
