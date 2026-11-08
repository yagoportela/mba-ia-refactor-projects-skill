function parsePort(value) {
  const port = Number(value);
  return Number.isInteger(port) && port > 0 ? port : 3000;
}

module.exports = {
  nodeEnv: process.env.NODE_ENV || "development",
  port: parsePort(process.env.PORT),
  databasePath: process.env.DATABASE_PATH || ":memory:",
  adminToken: process.env.ADMIN_TOKEN || "",
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
};
