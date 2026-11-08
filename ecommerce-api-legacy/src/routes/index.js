const express = require("express");

const { createCheckoutRoutes } = require("./checkoutRoutes");
const { createReportRoutes } = require("./reportRoutes");
const { createUserRoutes } = require("./userRoutes");

function createApiRouter(dependencies) {
  const router = express.Router();
  router.use(createCheckoutRoutes(dependencies));
  router.use(createReportRoutes(dependencies));
  router.use(createUserRoutes(dependencies));
  return router;
}

module.exports = { createApiRouter };
