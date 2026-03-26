import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [tab, setTab] = useState("stats");
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchStats();
    fetchUsers();
    fetchJobs();
    fetchApplications();
  }, []);

  const fetchStats = async () => {
    const { data } = await api.get("/admin/stats");
    setStats(data);
  };

  const fetchUsers = async () => {
    const { data } = await api.get("/admin/users");
    setUsers(data);
  };

  const fetchJobs = async () => {
    const { data } = await api.get("/admin/jobs");
    setJobs(data);
  };

  const fetchApplications = async () => {
    const { data } = await api.get("/admin/applications");
    setApplications(data);
  };

  const deleteUser = async (id) => {
    if (!window.confirm("Delete this user?")) return;
    try {
      await api.delete(`/admin/users/${id}`);
      setMessage("User deleted.");
      fetchUsers();
      fetchStats();
    } catch (err) {
      setMessage(err.response?.data?.error || "Failed to delete user");
    }
  };

  const deleteJob = async (id) => {
    if (!window.confirm("Delete this job?")) return;
    try {
      await api.delete(`/admin/jobs/${id}`);
      setMessage("Job deleted.");
      fetchJobs();
      fetchStats();
    } catch (err) {
      setMessage(err.response?.data?.error || "Failed to delete job");
    }
  };

  return (
    <div className="dashboard">
      <h2>Admin Dashboard — {user.name}</h2>
      {message && <p className="message">{message}</p>}

      <div className="admin-tabs">
        {["stats", "users", "jobs", "applications"].map((t) => (
          <button
            key={t}
            className={tab === t ? "btn-primary" : "btn-secondary"}
            onClick={() => setTab(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === "stats" && stats && (
        <div className="stats-grid">
          <div className="stat-card"><h3>{stats.total_users}</h3><p>Total Users</p></div>
          <div className="stat-card"><h3>{stats.total_seekers}</h3><p>Job Seekers</p></div>
          <div className="stat-card"><h3>{stats.total_recruiters}</h3><p>Recruiters</p></div>
          <div className="stat-card"><h3>{stats.total_jobs}</h3><p>Jobs Posted</p></div>
          <div className="stat-card"><h3>{stats.total_applications}</h3><p>Applications</p></div>
        </div>
      )}

      {tab === "users" && (
        <div className="dashboard-section">
          <h3>All Users ({users.length})</h3>
          <table className="app-table">
            <thead>
              <tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th>Action</th></tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>#{u.id}</td>
                  <td>{u.name}</td>
                  <td>{u.email}</td>
                  <td><span className={`status-badge ${u.role}`}>{u.role}</span></td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                  <td>
                    {u.role !== "admin" && (
                      <button className="btn-delete" onClick={() => deleteUser(u.id)}>Delete</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "jobs" && (
        <div className="dashboard-section">
          <h3>All Jobs ({jobs.length})</h3>
          <table className="app-table">
            <thead>
              <tr><th>ID</th><th>Title</th><th>Company</th><th>Location</th><th>Posted</th><th>Action</th></tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id}>
                  <td>#{j.id}</td>
                  <td>{j.title}</td>
                  <td>{j.company}</td>
                  <td>{j.location}</td>
                  <td>{new Date(j.posted_at).toLocaleDateString()}</td>
                  <td>
                    <button className="btn-delete" onClick={() => deleteJob(j.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "applications" && (
        <div className="dashboard-section">
          <h3>All Applications ({applications.length})</h3>
          <table className="app-table">
            <thead>
              <tr><th>ID</th><th>User</th><th>Job</th><th>Score</th><th>Status</th><th>Applied</th></tr>
            </thead>
            <tbody>
              {applications.map((a) => (
                <tr key={a.id}>
                  <td>#{a.id}</td>
                  <td>User #{a.user_id}</td>
                  <td>Job #{a.job_id}</td>
                  <td>{a.match_score}%</td>
                  <td><span className={`status-badge ${a.status}`}>{a.status}</span></td>
                  <td>{new Date(a.applied_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
