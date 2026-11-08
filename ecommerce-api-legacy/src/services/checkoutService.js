const auditLogModel = require("../models/auditLogModel");
const courseModel = require("../models/courseModel");
const enrollmentModel = require("../models/enrollmentModel");
const paymentModel = require("../models/paymentModel");
const userModel = require("../models/userModel");
const { AppError } = require("../utils/errors");
const { hashPassword, verifyPassword } = require("../utils/password");

class CheckoutService {
  constructor({ db, cache, paymentService, logger }) {
    this.db = db;
    this.cache = cache;
    this.paymentService = paymentService;
    this.logger = logger;
  }

  async execute(input) {
    const course = await courseModel.findActiveById(this.db, input.courseId);
    if (!course) {
      throw new AppError("Curso não encontrado", 404);
    }

    const existingUser = await userModel.findByEmail(this.db, input.email);
    if (existingUser && !verifyPassword(input.password, existingUser.pass)) {
      throw new AppError("Credenciais inválidas", 401);
    }
    if (!existingUser && !input.password) {
      throw new AppError("Senha é obrigatória", 400);
    }

    const paymentStatus = this.paymentService.process(input.card);
    if (paymentStatus === "DENIED") {
      throw new AppError("Pagamento recusado", 400);
    }

    let userId = existingUser ? existingUser.id : null;

    const enrollmentId = await this.db.transaction(async () => {
      if (!userId) {
        const created = await userModel.create(this.db, {
          name: input.name,
          email: input.email,
          passwordHash: hashPassword(input.password),
        });
        userId = created.lastID;
      }

      const enrollment = await enrollmentModel.create(this.db, userId, course.id);
      await paymentModel.create(this.db, enrollment.lastID, course.price, paymentStatus);
      await auditLogModel.create(
        this.db,
        `Checkout curso ${course.id} por ${userId}`
      );
      return enrollment.lastID;
    });

    this.cache.set(`last_checkout_${userId}`, course.title);
    this.logger.info("Checkout concluído", {
      enrollmentId,
      courseId: course.id,
      userId,
    });

    return { enrollmentId, userId, courseTitle: course.title };
  }
}

module.exports = { CheckoutService };
