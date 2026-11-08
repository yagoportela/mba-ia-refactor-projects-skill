const { validateId } = require("../utils/validators");

function createUserController({ userService }) {
  return {
    async deleteUser(req, res) {
      const userId = validateId(req.params.id, "Usuário");
      await userService.deleteUser(userId);
      res.status(200).json({
        message: "Usuário deletado e dados relacionados removidos",
        success: true,
      });
    },
  };
}

module.exports = { createUserController };
