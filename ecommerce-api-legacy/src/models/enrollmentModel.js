function create(db, userId, courseId) {
  return db.run(
    "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
    [userId, courseId]
  );
}

function findByCourseId(db, courseId) {
  return db.all(
    "SELECT id, user_id, course_id FROM enrollments WHERE course_id = ? ORDER BY id",
    [courseId]
  );
}

module.exports = { create, findByCourseId };
