const sqlite3 = require("sqlite3").verbose();

const { hashPassword } = require("../utils/password");

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    pass TEXT NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
  )`,
  `CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
  )`,
  `CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
  )`,
  `CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY,
    action TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
  "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
  "CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id)",
  "CREATE INDEX IF NOT EXISTS idx_enrollments_user ON enrollments(user_id)",
  "CREATE INDEX IF NOT EXISTS idx_payments_enrollment ON payments(enrollment_id)",
];

class Database {
  constructor(path) {
    this.path = path;
    this.connection = null;
    this.queue = Promise.resolve();
  }

  open() {
    return new Promise((resolve, reject) => {
      this.connection = new sqlite3.Database(this.path, (error) => {
        if (error) {
          return reject(error);
        }
        this.connection.run("PRAGMA foreign_keys = ON", (pragmaError) => {
          if (pragmaError) {
            return reject(pragmaError);
          }
          return resolve();
        });
      });
    });
  }

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.run(sql, params, function onRun(error) {
        if (error) {
          return reject(error);
        }
        return resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.get(sql, params, (error, row) => {
        if (error) {
          return reject(error);
        }
        return resolve(row);
      });
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.all(sql, params, (error, rows) => {
        if (error) {
          return reject(error);
        }
        return resolve(rows);
      });
    });
  }

  transaction(callback) {
    const execute = async () => {
      await this.run("BEGIN IMMEDIATE");
      try {
        const result = await callback();
        await this.run("COMMIT");
        return result;
      } catch (error) {
        try {
          await this.run("ROLLBACK");
        } catch (rollbackError) {
          // A falha no rollback não deve mascarar o erro original.
        }
        throw error;
      }
    };

    const next = this.queue.then(execute, execute);
    this.queue = next.catch(() => undefined);
    return next;
  }

  close() {
    return new Promise((resolve, reject) => {
      if (!this.connection) {
        return resolve();
      }
      this.connection.close((error) => (error ? reject(error) : resolve()));
    });
  }
}

async function seedDatabase(db) {
  await db.transaction(async () => {
    const user = await db.run(
      "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
      ["Leonan", "leonan@fullcycle.com.br", hashPassword("123")]
    );
    const cleanArchitecture = await db.run(
      "INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
      ["Clean Architecture", 997.0, 1]
    );
    await db.run(
      "INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
      ["Docker", 497.0, 1]
    );
    const enrollment = await db.run(
      "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
      [user.lastID, cleanArchitecture.lastID]
    );
    await db.run(
      "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
      [enrollment.lastID, 997.0, "PAID"]
    );
  });
}

async function initDatabase(db) {
  for (const statement of SCHEMA) {
    await db.run(statement);
  }

  const { count } = await db.get("SELECT COUNT(*) AS count FROM users");
  if (count === 0) {
    await seedDatabase(db);
  }
}

module.exports = { Database, initDatabase };
