import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({
    title: "", company: "", description: "",
    required_skills: "", location: "", experience_required: "",
  });

  useEffect(() => {
    fetchJobs();
    fetchApplications();
  }, []);

  const fetchJobs = async () => {
    try {
      const { data } = await api.get("/jobs/");
      setJobs(data);
    } catch {
      // ignore
    }
  };

  const fetchApplications = async () => {
    try {
      const { data } = await api.get("/jobs/recruiter/applications");
      setApplications(data);
    } catch {
      // ignore
    }
  };

  const fetchCandidates = async (jobId) => {
    setSelectedJob(jobId);
    try {
      const { data } = await api.get(`/match/candidates/${jobId}`);
      setCandidates(data);
    } catch {
      setCandidates([]);
    }
  };

  const handlePostJob = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await api.post("/jobs/", form);
      setMessage("Job posted successfully!");
      setForm({ title: "", company: "", description: "", required_skills: "", location: "", experience_required: "" });
      fetchJobs();
    } catch (err) {
      setMessage(err.response?.data?.error || "Failed to post job");
    }
  };

  const handleStatusUpdate = async (appId, status) => {
    try {
      await api.patch(`/jobs/applications/${appId}/status`, { status });
      fetchApplications();
    } catch {
      // ignore
    }
  };

  return (
    <div className="dashboard">
      <h2>Recruiter Dashboard — {user.name}</h2>

      <section className="dashboard-section">
        <h3>Post a New Job</h3>
        <form className="job-form" onSubmit={handlePostJob}>
          <input placeholder="Job Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          <input placeholder="Company" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required />
          <input placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <input placeholder="Experience Required (e.g. 2 years)" value={form.experience_required} onChange={(e) => setForm({ ...form, experience_required: e.target.value })} />
          <input placeholder="Required Skills (comma-separated)" value={form.required_skills} onChange={(e) => setForm({ ...form, required_skills: e.target.value })} required />
          <textarea placeholder="Job Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required rows={4} />
          <button type="submit" className="btn-primary">Post Job</button>
        </form>
        {message && <p className="message">{message}</p>}
      </section>

      <section className="dashboard-section">
        <h3>Your Job Postings</h3>
        {jobs.length === 0 ? <p>No jobs posted yet.</p> : (
          <div className="job-list">
            {jobs.map((job) => (
              <div key={job.id} className="job-card">
                <h4>{job.title} — {job.company}</h4>
                <p>{job.location} | {job.experience_required}</p>
                <p>Skills: {job.required_skills.join(", ")}</p>
                <button className="btn-secondary" onClick={() => fetchCandidates(job.id)}>
                  View AI Candidates
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {selectedJob && (
        <section className="dashboard-section">
          <h3>AI-Recommended Candidates for Job #{selectedJob}</h3>
          {candidates.length === 0 ? <p>No candidates found.</p> : (
            <div className="job-list">
              {candidates.map((c, i) => (
                <div key={i} className="job-card">
                  <div className="job-header">
                    <h4>Candidate #{c.user_id}</h4>
                    <span className="match-badge">{c.match_score}% match</span>
                  </div>
                  <p>Skills: {c.skills.join(", ")}</p>
                  <p>Experience: {c.experience}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      <section className="dashboard-section">
        <h3>Applications</h3>
        {applications.length === 0 ? <p>No applications yet.</p> : (
          <table className="app-table">
            <thead>
              <tr>
                <th>App ID</th><th>Candidate</th><th>Job</th><th>Score</th><th>Status</th><th>Action</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((a) => (
                <tr key={a.application_id}>
                  <td>#{a.application_id}</td>
                  <td>User #{a.user_id}</td>
                  <td>Job #{a.job_id}</td>
                  <td>{a.match_score}%</td>
                  <td><span className={`status-badge ${a.status}`}>{a.status}</span></td>
                  <td>
                    <select
                      value={a.status}
                      onChange={(e) => handleStatusUpdate(a.application_id, e.target.value)}
                    >
                      <option value="applied">Applied</option>
                      <option value="shortlisted">Shortlisted</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
