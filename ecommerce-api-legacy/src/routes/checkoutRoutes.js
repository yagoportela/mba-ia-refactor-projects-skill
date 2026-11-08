const express = require("express");

const asyncHandler = require("../middlewares/asyncHandler");

function createCheckoutRoutes({ checkoutController }) {
  const router = express.Router();
  router.post("/checkout", asyncHandler(checkoutController.checkout));
  return router;
}

module.exports = { createCheckoutRoutes };
