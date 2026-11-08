function findByEmail(db, email) {
  return db.get(
    "SELECT id, name, email, pass FROM users WHERE email = ?",
    [email]
  );
}

function findById(db, id) {
  return db.get("SELECT id, name, email FROM users WHERE id = ?", [id]);
}

function create(db, { name, email, passwordHash }) {
  return db.run(
    "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
    [name, email, passwordHash]
  );
}

async function removeDependents(db, userId) {
  await db.run(
    "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)",
    [userId]
  );
  await db.run("DELETE FROM enrollments WHERE user_id = ?", [userId]);
}

function remove(db, userId) {
  return db.run("DELETE FROM users WHERE id = ?", [userId]);
}

module.exports = {
  findByEmail,
  findById,
  create,
  removeDependents,
  remove,
};
