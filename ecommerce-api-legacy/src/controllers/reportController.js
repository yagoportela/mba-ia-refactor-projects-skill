function createReportController({ reportService }) {
  return {
    async financialReport(req, res) {
      const report = await reportService.financialReport();
      res.status(200).json(report);
    },
  };
}

module.exports = { createReportController };
