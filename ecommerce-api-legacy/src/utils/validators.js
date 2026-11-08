const { AppError } = require("./errors");

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const CARD_RE = /^\d{13,19}$/;

function validateCheckout(body) {
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    throw new AppError("Dados inválidos", 400);
  }

  const name = body.usr ?? body.name;
  const email = body.eml ?? body.email;
  const password = body.pwd ?? body.password ?? "";
  const courseIdRaw = body.c_id ?? body.courseId;
  const cardRaw = body.card;

  if (!name || !email || courseIdRaw === undefined || courseIdRaw === null || !cardRaw) {
    throw new AppError("Bad Request", 400);
  }

  if (typeof name !== "string" || name.trim().length < 2) {
    throw new AppError("Nome inválido", 400);
  }

  if (typeof email !== "string" || !EMAIL_RE.test(email.trim().toLowerCase())) {
    throw new AppError("E-mail inválido", 400);
  }

  const courseId = Number(courseIdRaw);
  if (!Number.isInteger(courseId) || courseId <= 0) {
    throw new AppError("Curso inválido", 400);
  }

  const card = String(cardRaw).replace(/\s/g, "");
  if (!CARD_RE.test(card)) {
    throw new AppError("Cartão inválido", 400);
  }

  if (password !== "" && typeof password !== "string") {
    throw new AppError("Senha inválida", 400);
  }

  return {
    name: name.trim(),
    email: email.trim().toLowerCase(),
    password: String(password),
    courseId,
    card,
  };
}

function validateId(value, field = "id") {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new AppError(`${field} inválido`, 400);
  }
  return parsed;
}

module.exports = { validateCheckout, validateId };
