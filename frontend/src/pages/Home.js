import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="home">
      <section className="hero">
        <h1>Find Jobs That Match Your Skills</h1>
        <p>
          SkillMatch AI uses artificial intelligence to connect job seekers with
          the most relevant opportunities — beyond simple keyword matching.
        </p>
        <div className="hero-actions">
          <Link to="/register" className="btn-primary">Get Started</Link>
          <Link to="/jobs" className="btn-secondary">Browse Jobs</Link>
        </div>
      </section>

      <section className="features">
        <div className="feature-card">
          <h3>AI Resume Analysis</h3>
          <p>Upload your resume and let our AI extract your skills automatically.</p>
        </div>
        <div className="feature-card">
          <h3>Smart Matching</h3>
          <p>Get a match score for every job based on your actual skill profile.</p>
        </div>
        <div className="feature-card">
          <h3>For Recruiters</h3>
          <p>Post jobs and receive AI-ranked candidate recommendations instantly.</p>
        </div>
      </section>
    </div>
  );
}
