const auditLogModel = require("../models/auditLogModel");
const userModel = require("../models/userModel");
const { AppError } = require("../utils/errors");

class UserService {
  constructor({ db }) {
    this.db = db;
  }

  async deleteUser(userId) {
    const user = await userModel.findById(this.db, userId);
    if (!user) {
      throw new AppError("Usuário não encontrado", 404);
    }

    await this.db.transaction(async () => {
      await userModel.removeDependents(this.db, userId);
      await userModel.remove(this.db, userId);
      await auditLogModel.create(this.db, `Usuário ${userId} deletado`);
    });

    return { userId };
  }
}

module.exports = { UserService };
