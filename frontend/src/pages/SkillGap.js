import { useState, useEffect } from "react";
import api from "../api";

export default function SkillGap() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/jobs/").then(({ data }) => setJobs(data)).catch(() => {});
  }, []);

  const analyze = async () => {
    if (!selectedJob) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const { data } = await api.get(`/enhance/skill-gap/${selectedJob}`);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.error || "Analysis failed. Upload your resume first.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <h2>Skill Gap Analysis</h2>

      <div className="dashboard-section">
        <h3>Select a Job to Analyze</h3>
        <div className="filters">
          <select value={selectedJob} onChange={(e) => setSelectedJob(e.target.value)}>
            <option value="">-- Select a Job --</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>{j.title} — {j.company}</option>
            ))}
          </select>
          <button className="btn-primary" onClick={analyze} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      {result && (
        <>
          <div className="dashboard-section">
            <h3>{result.job_title} — Match Score: <span className="match-badge">{result.match_score}%</span></h3>
            <div className="skill-gap-grid">
              <div className="skill-box matched">
                <h4>✅ Skills You Have ({result.matched_skills.length})</h4>
                {result.matched_skills.length === 0 ? <p>None matched</p> : (
                  <div className="skill-tags">
                    {result.matched_skills.map((s) => <span key={s} className="skill-tag green">{s}</span>)}
                  </div>
                )}
              </div>
              <div className="skill-box missing">
                <h4>❌ Skills You Need ({result.missing_skills.length})</h4>
                {result.missing_skills.length === 0 ? <p>You have all required skills!</p> : (
                  <div className="skill-tags">
                    {result.missing_skills.map((s) => <span key={s} className="skill-tag red">{s}</span>)}
                  </div>
                )}
              </div>
            </div>
          </div>

          {result.course_recommendations.length > 0 && (
            <div className="dashboard-section">
              <h3>📚 Recommended Courses to Bridge the Gap</h3>
              <div className="course-list">
                {result.course_recommendations.map((c, i) => (
                  <div key={i} className="course-card">
                    <div>
                      <p className="course-skill">Skill: <strong>{c.skill}</strong></p>
                      <p className="course-name">{c.course}</p>
                      <span className="platform-badge">{c.platform}</span>
                    </div>
                    <a href={c.url} target="_blank" rel="noreferrer" className="btn-primary">
                      Learn Now
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
