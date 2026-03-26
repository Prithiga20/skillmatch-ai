import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";
import OnboardingTour from "../components/OnboardingTour";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [funnels, setFunnels] = useState({});
  const [companyProfile, setCompanyProfile] = useState(null);
  const [showCompanyForm, setShowCompanyForm] = useState(false);
  const [companyForm, setCompanyForm] = useState({ company_name: "", industry: "", website: "", location: "", description: "" });
  const [message, setMessage] = useState("");
  const [showTour, setShowTour] = useState(!localStorage.getItem("tour_recruiter"));
  const [form, setForm] = useState({ title: "", company: "", description: "", required_skills: "", location: "", experience_required: "", expiry_date: "" });

  useEffect(() => {
    fetchJobs();
    fetchApplications();
    fetchCompanyProfile();
  }, []);

  const fetchJobs = async () => {
    try {
      const { data } = await api.get("/jobs/");
      setJobs(data);
    } catch { }
  };

  const fetchApplications = async () => {
    try {
      const { data } = await api.get("/jobs/recruiter/applications");
      setApplications(data);
    } catch { }
  };

  const fetchCompanyProfile = async () => {
    try {
      const { data } = await api.get("/enhance/company-profile");
      setCompanyProfile(data);
      setCompanyForm(data);
    } catch { }
  };

  const fetchCandidates = async (jobId) => {
    setSelectedJob(jobId);
    try {
      const { data } = await api.get(`/match/candidates/${jobId}`);
      setCandidates(data);
      const { data: funnel } = await api.get(`/enhance/hiring-funnel/${jobId}`);
      setFunnels((prev) => ({ ...prev, [jobId]: funnel }));
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
      setForm({ title: "", company: "", description: "", required_skills: "", location: "", experience_required: "", expiry_date: "" });
      fetchJobs();
    } catch (err) {
      setMessage(err.response?.data?.error || "Failed to post job");
    }
  };

  const handleToggleStatus = async (jobId) => {
    try {
      const { data } = await api.patch(`/jobs/${jobId}/toggle-status`);
      fetchJobs();
      setMessage(`Job ${data.status}`);
    } catch { }
  };

  const handleStatusUpdate = async (appId, status) => {
    try {
      await api.patch(`/jobs/applications/${appId}/status`, { status });
      fetchApplications();
    } catch { }
  };

  const handleSaveCompany = async (e) => {
    e.preventDefault();
    try {
      await api.post("/enhance/company-profile", companyForm);
      setMessage("Company profile saved!");
      setShowCompanyForm(false);
      fetchCompanyProfile();
    } catch { }
  };

  const completeTour = () => {
    localStorage.setItem("tour_recruiter", "done");
    setShowTour(false);
  };

  return (
    <div className="dashboard">
      {showTour && <OnboardingTour role="recruiter" onComplete={completeTour} />}
      <h2>Recruiter Dashboard — {user.name}</h2>

      {/* Feature 18: Company Profile */}
      <section className="dashboard-section">
        <div className="section-header">
          <h3>Company Profile</h3>
          <button className="btn-secondary" onClick={() => setShowCompanyForm(!showCompanyForm)}>
            {showCompanyForm ? "Cancel" : "Edit Profile"}
          </button>
        </div>
        {showCompanyForm ? (
          <form className="job-form" onSubmit={handleSaveCompany}>
            <input placeholder="Company Name" value={companyForm.company_name} onChange={(e) => setCompanyForm({ ...companyForm, company_name: e.target.value })} />
            <input placeholder="Industry" value={companyForm.industry} onChange={(e) => setCompanyForm({ ...companyForm, industry: e.target.value })} />
            <input placeholder="Website" value={companyForm.website} onChange={(e) => setCompanyForm({ ...companyForm, website: e.target.value })} />
            <input placeholder="Location" value={companyForm.location} onChange={(e) => setCompanyForm({ ...companyForm, location: e.target.value })} />
            <textarea rows={3} placeholder="Company Description" value={companyForm.description} onChange={(e) => setCompanyForm({ ...companyForm, description: e.target.value })} />
            <button type="submit" className="btn-primary">Save</button>
          </form>
        ) : companyProfile?.company_name ? (
          <div className="profile-card">
            <p><strong>{companyProfile.company_name}</strong> — {companyProfile.industry}</p>
            <p>{companyProfile.location} | <a href={companyProfile.website} target="_blank" rel="noreferrer">{companyProfile.website}</a></p>
            <p>{companyProfile.description}</p>
          </div>
        ) : (
          <p>No company profile set. Click Edit Profile to add one.</p>
        )}
      </section>

      <section className="dashboard-section">
        <h3>Post a New Job</h3>
        <form className="job-form" onSubmit={handlePostJob}>
          <input placeholder="Job Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          <input placeholder="Company" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required />
          <input placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <input placeholder="Experience Required (e.g. 2 years)" value={form.experience_required} onChange={(e) => setForm({ ...form, experience_required: e.target.value })} />
          <input placeholder="Required Skills (comma-separated)" value={form.required_skills} onChange={(e) => setForm({ ...form, required_skills: e.target.value })} required />
          <input type="date" placeholder="Expiry Date" value={form.expiry_date} onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} />
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
                <div className="job-header">
                  <h4>{job.title} — {job.company}</h4>
                  <span className={`status-badge ${job.status}`}>{job.status}</span>
                </div>
                <p>{job.location} | {job.experience_required}</p>
                <p>Skills: {job.required_skills.join(", ")}</p>
                {job.expiry_date && <p>Expires: {job.expiry_date}</p>}
                <p className="views-count">👁 {job.views} views</p>
                <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                  <button className="btn-secondary" onClick={() => fetchCandidates(job.id)}>View AI Candidates</button>
                  <button className={job.status === "open" ? "btn-delete" : "btn-primary"} onClick={() => handleToggleStatus(job.id)}>
                    {job.status === "open" ? "Close Job" : "Reopen Job"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Feature 14: Hiring Funnel */}
      {selectedJob && funnels[selectedJob] && (
        <section className="dashboard-section">
          <h3>Hiring Funnel</h3>
          <div className="funnel">
            <div className="funnel-step applied">
              <span>{funnels[selectedJob].applied}</span>
              <p>Applied</p>
            </div>
            <div className="funnel-arrow">→</div>
            <div className="funnel-step shortlisted">
              <span>{funnels[selectedJob].shortlisted}</span>
              <p>Shortlisted</p>
            </div>
            <div className="funnel-arrow">→</div>
            <div className="funnel-step rejected">
              <span>{funnels[selectedJob].rejected}</span>
              <p>Rejected</p>
            </div>
          </div>
        </section>
      )}

      {selectedJob && (
        <section className="dashboard-section">
          <h3>AI-Recommended Candidates</h3>
          {candidates.length === 0 ? <p>No candidates found.</p> : (
            <div className="job-list">
              {candidates.map((c, i) => (
                <div key={i} className="job-card">
                  <div className="job-header">
                    <h4>Candidate #{c.user_id.slice(-6)}</h4>
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
              <tr><th>Candidate</th><th>Job</th><th>Score</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              {applications.map((a) => (
                <tr key={a.application_id}>
                  <td>#{a.user_id.slice(-6)}</td>
                  <td>#{a.job_id.slice(-6)}</td>
                  <td>{a.match_score}%</td>
                  <td><span className={`status-badge ${a.status}`}>{a.status}</span></td>
                  <td>
                    <select value={a.status} onChange={(e) => handleStatusUpdate(a.application_id, e.target.value)}>
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
