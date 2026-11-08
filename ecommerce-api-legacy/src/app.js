const express = require("express");

const config = require("./config");
const { createCheckoutController } = require("./controllers/checkoutController");
const { createReportController } = require("./controllers/reportController");
const { createUserController } = require("./controllers/userController");
const { Database, initDatabase } = require("./db/database");
const { createRequireAdmin } = require("./middlewares/auth");
const { errorHandler, notFoundHandler } = require("./middlewares/errorHandler");
const { createApiRouter } = require("./routes");
const { CacheService } = require("./services/cacheService");
const { CheckoutService } = require("./services/checkoutService");
const { PaymentService } = require("./services/paymentService");
const { ReportService } = require("./services/reportService");
const { UserService } = require("./services/userService");
const logger = require("./utils/logger");

async function createApp(overrides = {}) {
  const settings = { ...config, ...overrides };
  const app = express();
  app.use(express.json());

  const db = new Database(settings.databasePath);
  await db.open();
  await initDatabase(db);

  const cache = new CacheService();
  const paymentService = new PaymentService();
  const checkoutService = new CheckoutService({
    db,
    cache,
    paymentService,
    logger,
  });
  const reportService = new ReportService({ db });
  const userService = new UserService({ db });

  const checkoutController = createCheckoutController({ checkoutService });
  const reportController = createReportController({ reportService });
  const userController = createUserController({ userService });
  const requireAdmin = createRequireAdmin(settings);

  app.get("/health", (req, res) => {
    res.status(200).json({ status: "ok" });
  });

  app.use(
    "/api",
    createApiRouter({
      checkoutController,
      reportController,
      userController,
      requireAdmin,
    })
  );

  app.use(notFoundHandler);
  app.use(errorHandler);

  app.locals.db = db;
  return app;
}

async function start() {
  const app = await createApp();
  app.listen(config.port, () => {
    logger.info("Frankenstein LMS rodando", {
      port: config.port,
      database: config.databasePath,
    });
  });
}

if (require.main === module) {
  start().catch((error) => {
    logger.error("Falha ao iniciar a aplicação", { error: error.message });
    process.exit(1);
  });
}

module.exports = { createApp, start };
