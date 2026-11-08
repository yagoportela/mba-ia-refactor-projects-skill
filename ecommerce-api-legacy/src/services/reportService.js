const reportModel = require("../models/reportModel");

class ReportService {
  constructor({ db }) {
    this.db = db;
  }

  async financialReport() {
    const rows = await reportModel.financialRows(this.db);
    const courses = new Map();

    for (const row of rows) {
      if (!courses.has(row.course_id)) {
        courses.set(row.course_id, {
          course: row.course_title,
          revenue: 0,
          students: [],
        });
      }

      if (row.enrollment_id) {
        const course = courses.get(row.course_id);
        const amount = row.payment_amount || 0;
        if (row.payment_status === "PAID") {
          course.revenue += amount;
        }
        course.students.push({
          student: row.student_name || "Unknown",
          paid: amount,
        });
      }
    }

    return Array.from(courses.values());
  }
}

module.exports = { ReportService };
