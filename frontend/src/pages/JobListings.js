import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api";

export default function JobListings() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [filters, setFilters] = useState({ skill: "", location: "" });
  const [searchHistory, setSearchHistory] = useState([]);
  const [similarJobs, setSimilarJobs] = useState({});
  const [expandedJob, setExpandedJob] = useState(null);

  useEffect(() => {
    fetchJobs();
    if (user) fetchSearchHistory();
  }, []);

  const fetchJobs = async () => {
    try {
      const { data } = await api.get("/jobs/", { params: filters });
      setJobs(data);
    } catch { }
  };

  const fetchSearchHistory = async () => {
    try {
      const { data } = await api.get("/enhance/search-history");
      setSearchHistory(data);
    } catch { }
  };

  const handleSearch = async () => {
    fetchJobs();
    if (user && (filters.skill || filters.location)) {
      const query = [filters.skill, filters.location].filter(Boolean).join(", ");
      try {
        await api.post("/enhance/search-history", { query });
        fetchSearchHistory();
      } catch { }
    }
  };

  const clearHistory = async () => {
    try {
      await api.delete("/enhance/search-history");
      setSearchHistory([]);
    } catch { }
  };

  const applyHistorySearch = (query) => {
    const parts = query.split(", ");
    setFilters({ skill: parts[0] || "", location: parts[1] || "" });
  };

  const fetchSimilarJobs = async (jobId) => {
    if (similarJobs[jobId]) {
      setExpandedJob(expandedJob === jobId ? null : jobId);
      return;
    }
    try {
      const { data } = await api.get(`/enhance/similar-jobs/${jobId}`);
      setSimilarJobs((prev) => ({ ...prev, [jobId]: data }));
      setExpandedJob(jobId);
    } catch { }
  };

  const handleApply = async (jobId) => {
    if (!user) return navigate("/login");
    try {
      await api.post(`/jobs/${jobId}/apply`);
      alert("Applied successfully!");
    } catch (err) {
      alert(err.response?.data?.error || "Application failed");
    }
  };

  return (
    <div className="jobs-page">
      <h2>Job Listings</h2>

      <div className="filters">
        <input placeholder="Filter by skill" value={filters.skill} onChange={(e) => setFilters({ ...filters, skill: e.target.value })} />
        <input placeholder="Filter by location" value={filters.location} onChange={(e) => setFilters({ ...filters, location: e.target.value })} />
        <button className="btn-primary" onClick={handleSearch}>Search</button>
      </div>

      {/* Feature 17: Search History */}
      {user && searchHistory.length > 0 && (
        <div className="search-history">
          <span>Recent searches:</span>
          {searchHistory.map((q, i) => (
            <button key={i} className="history-tag" onClick={() => applyHistorySearch(q)}>{q}</button>
          ))}
          <button className="btn-link" onClick={clearHistory}>Clear</button>
        </div>
      )}

      {jobs.length === 0 ? (
        <p>No jobs found.</p>
      ) : (
        <div className="job-list">
          {jobs.map((job) => (
            <div key={job.id} className="job-card">
              <div className="job-header">
                <h4>{job.title}</h4>
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  <span className="views-count">👁 {job.views}</span>
                  {job.expiry_date && <span className="expiry-tag">Expires: {job.expiry_date}</span>}
                </div>
              </div>
              <p className="company">{job.company} — {job.location}</p>
              <p>{job.description.slice(0, 120)}...</p>
              <p><strong>Skills:</strong> {job.required_skills.join(", ")}</p>
              <p><strong>Experience:</strong> {job.experience_required || "Not specified"}</p>

              <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.75rem", flexWrap: "wrap" }}>
                {user?.role === "seeker" && (
                  <button className="btn-primary" onClick={() => handleApply(job.id)}>Apply</button>
                )}
                {/* Feature 5: Similar Jobs */}
                <button className="btn-secondary" onClick={() => fetchSimilarJobs(job.id)}>
                  {expandedJob === job.id ? "Hide Similar" : "Similar Jobs"}
                </button>
              </div>

              {expandedJob === job.id && similarJobs[job.id] && (
                <div className="similar-jobs">
                  <p><strong>Similar Jobs:</strong></p>
                  {similarJobs[job.id].length === 0 ? <p>No similar jobs found.</p> : (
                    similarJobs[job.id].map((s) => (
                      <div key={s.id} className="similar-job-item">
                        <span>{s.title} — {s.company}</span>
                        <span className="match-badge">{s.match_score}%</span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
