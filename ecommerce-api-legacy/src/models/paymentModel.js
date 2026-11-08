function create(db, enrollmentId, amount, status) {
  return db.run(
    "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
    [enrollmentId, amount, status]
  );
}

function findByEnrollmentId(db, enrollmentId) {
  return db.get(
    "SELECT amount, status FROM payments WHERE enrollment_id = ?",
    [enrollmentId]
  );
}

module.exports = { create, findByEnrollmentId };
