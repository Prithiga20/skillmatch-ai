import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";

export default function SeekerDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [applications, setApplications] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchProfile();
    fetchApplications();
  }, []);

  const fetchProfile = async () => {
    try {
      const { data } = await api.get("/resume/profile");
      setProfile(data);
      fetchRecommendations();
    } catch {
      // no resume yet
    }
  };

  const fetchRecommendations = async () => {
    try {
      const { data } = await api.get("/match/recommendations");
      setRecommendations(data);
    } catch {
      // ignore
    }
  };

  const fetchApplications = async () => {
    try {
      const { data } = await api.get("/jobs/applications");
      setApplications(data);
    } catch {
      // ignore
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setMessage("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const { data } = await api.post("/resume/upload", formData);
      setProfile(data);
      setMessage("Resume uploaded successfully!");
      fetchRecommendations();
    } catch (err) {
      setMessage(err.response?.data?.error || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleApply = async (jobId) => {
    try {
      await api.post(`/jobs/${jobId}/apply`);
      fetchApplications();
      setMessage("Applied successfully!");
    } catch (err) {
      setMessage(err.response?.data?.error || "Application failed");
    }
  };

  const appliedJobIds = new Set(applications.map((a) => a.job_id));

  return (
    <div className="dashboard">
      <h2>Welcome, {user.name}</h2>

      <section className="dashboard-section">
        <h3>Your Profile</h3>
        {profile ? (
          <div className="profile-card">
            <p><strong>Skills:</strong> {profile.skills.join(", ") || "None detected"}</p>
            <p><strong>Experience:</strong> {profile.experience}</p>
            <p><strong>Education:</strong> {profile.education}</p>
          </div>
        ) : (
          <p>No resume uploaded yet.</p>
        )}
        <label className="btn-secondary upload-btn">
          {uploading ? "Uploading..." : "Upload Resume (PDF/DOCX)"}
          <input type="file" accept=".pdf,.docx,.doc,.txt" onChange={handleUpload} hidden />
        </label>
        {message && <p className="message">{message}</p>}
      </section>

      <section className="dashboard-section">
        <h3>Recommended Jobs</h3>
        {recommendations.length === 0 ? (
          <p>Upload a resume to get personalized recommendations.</p>
        ) : (
          <div className="job-list">
            {recommendations.map((job) => (
              <div key={job.id} className="job-card">
                <div className="job-header">
                  <h4>{job.title}</h4>
                  <span className="match-badge">{job.match_score}% match</span>
                </div>
                <p className="company">{job.company} — {job.location}</p>
                <p className="skills-required">
                  Skills: {job.required_skills.join(", ")}
                </p>
                {appliedJobIds.has(job.id) ? (
                  <span className="applied-tag">Applied</span>
                ) : (
                  <button className="btn-primary" onClick={() => handleApply(job.id)}>
                    Apply
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="dashboard-section">
        <h3>My Applications</h3>
        {applications.length === 0 ? (
          <p>No applications yet.</p>
        ) : (
          <table className="app-table">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Match Score</th>
                <th>Status</th>
                <th>Applied At</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((a) => (
                <tr key={a.application_id}>
                  <td>#{a.job_id}</td>
                  <td>{a.match_score}%</td>
                  <td><span className={`status-badge ${a.status}`}>{a.status}</span></td>
                  <td>{new Date(a.applied_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
