const express = require("express");

const asyncHandler = require("../middlewares/asyncHandler");

function createUserRoutes({ userController, requireAdmin }) {
  const router = express.Router();
  router.delete(
    "/users/:id",
    requireAdmin,
    asyncHandler(userController.deleteUser)
  );
  return router;
}

module.exports = { createUserRoutes };
