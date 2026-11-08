class PaymentService {
  process(card) {
    return String(card).startsWith("4") ? "PAID" : "DENIED";
  }
}

module.exports = { PaymentService };
