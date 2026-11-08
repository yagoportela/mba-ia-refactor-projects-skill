function findActiveById(db, courseId) {
  return db.get(
    "SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1",
    [courseId]
  );
}

function listAll(db) {
  return db.all("SELECT id, title, price, active FROM courses ORDER BY id");
}

module.exports = { findActiveById, listAll };
