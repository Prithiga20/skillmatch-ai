import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">SkillMatch AI</Link>
      <div className="navbar-links">
        <Link to="/jobs">Jobs</Link>
        {user ? (
          <>
            <Link to={user.role === "recruiter" ? "/recruiter" : user.role === "admin" ? "/admin" : "/dashboard"}>
              Dashboard
            </Link>
            <button onClick={handleLogout} className="btn-link">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register" className="btn-primary">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}
