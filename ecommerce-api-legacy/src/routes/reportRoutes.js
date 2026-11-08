const express = require("express");

const asyncHandler = require("../middlewares/asyncHandler");

function createReportRoutes({ reportController, requireAdmin }) {
  const router = express.Router();
  router.get(
    "/admin/financial-report",
    requireAdmin,
    asyncHandler(reportController.financialReport)
  );
  return router;
}

module.exports = { createReportRoutes };
