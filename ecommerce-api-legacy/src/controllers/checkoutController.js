const { validateCheckout } = require("../utils/validators");

function createCheckoutController({ checkoutService }) {
  return {
    async checkout(req, res) {
      const input = validateCheckout(req.body);
      const result = await checkoutService.execute(input);
      res.status(200).json({
        msg: "Sucesso",
        enrollment_id: result.enrollmentId,
      });
    },
  };
}

module.exports = { createCheckoutController };
