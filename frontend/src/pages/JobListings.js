import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api";

export default function JobListings() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [filters, setFilters] = useState({ skill: "", location: "" });

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const { data } = await api.get("/jobs/", { params: filters });
      setJobs(data);
    } catch {
      // ignore
    }
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
        <input
          placeholder="Filter by skill"
          value={filters.skill}
          onChange={(e) => setFilters({ ...filters, skill: e.target.value })}
        />
        <input
          placeholder="Filter by location"
          value={filters.location}
          onChange={(e) => setFilters({ ...filters, location: e.target.value })}
        />
        <button className="btn-primary" onClick={fetchJobs}>Search</button>
      </div>

      {jobs.length === 0 ? (
        <p>No jobs found.</p>
      ) : (
        <div className="job-list">
          {jobs.map((job) => (
            <div key={job.id} className="job-card">
              <h4>{job.title}</h4>
              <p className="company">{job.company} — {job.location}</p>
              <p>{job.description.slice(0, 120)}...</p>
              <p><strong>Skills:</strong> {job.required_skills.join(", ")}</p>
              <p><strong>Experience:</strong> {job.experience_required || "Not specified"}</p>
              {user?.role === "seeker" && (
                <button className="btn-primary" onClick={() => handleApply(job.id)}>
                  Apply
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
