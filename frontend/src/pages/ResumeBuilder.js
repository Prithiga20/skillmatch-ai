import { useState } from "react";

export default function ResumeBuilder() {
  const [form, setForm] = useState({
    name: "", email: "", phone: "", location: "",
    summary: "", skills: "", experience: "", education: "", certifications: "",
  });

  const update = (field, val) => setForm({ ...form, [field]: val });

  const handlePrint = () => window.print();

  return (
    <div className="dashboard">
      <h2>Resume Builder</h2>
      <div className="resume-builder-layout">

        <div className="dashboard-section resume-form">
          <h3>Fill Your Details</h3>

          <label>Full Name</label>
          <input placeholder="John Doe" value={form.name} onChange={(e) => update("name", e.target.value)} />

          <label>Email</label>
          <input placeholder="john@email.com" value={form.email} onChange={(e) => update("email", e.target.value)} />

          <label>Phone</label>
          <input placeholder="+1 234 567 8900" value={form.phone} onChange={(e) => update("phone", e.target.value)} />

          <label>Location</label>
          <input placeholder="City, Country" value={form.location} onChange={(e) => update("location", e.target.value)} />

          <label>Professional Summary</label>
          <textarea rows={3} placeholder="Brief summary about yourself..." value={form.summary} onChange={(e) => update("summary", e.target.value)} />

          <label>Skills (comma-separated)</label>
          <input placeholder="Python, React, SQL..." value={form.skills} onChange={(e) => update("skills", e.target.value)} />

          <label>Work Experience</label>
          <textarea rows={4} placeholder="Job Title at Company (Year - Year)&#10;- Achievement 1&#10;- Achievement 2" value={form.experience} onChange={(e) => update("experience", e.target.value)} />

          <label>Education</label>
          <textarea rows={3} placeholder="Degree, University (Year)" value={form.education} onChange={(e) => update("education", e.target.value)} />

          <label>Certifications</label>
          <textarea rows={2} placeholder="Certification Name, Issuer (Year)" value={form.certifications} onChange={(e) => update("certifications", e.target.value)} />

          <button className="btn-primary" onClick={handlePrint} style={{ marginTop: "1rem" }}>
            Download / Print Resume
          </button>
        </div>

        <div className="resume-preview" id="resume-preview">
          <div className="resume-header">
            <h1>{form.name || "Your Name"}</h1>
            <p>{[form.email, form.phone, form.location].filter(Boolean).join(" | ")}</p>
          </div>

          {form.summary && (
            <div className="resume-section">
              <h3>Professional Summary</h3>
              <p>{form.summary}</p>
            </div>
          )}

          {form.skills && (
            <div className="resume-section">
              <h3>Skills</h3>
              <div className="skill-tags">
                {form.skills.split(",").map((s, i) => (
                  <span key={i} className="skill-tag green">{s.trim()}</span>
                ))}
              </div>
            </div>
          )}

          {form.experience && (
            <div className="resume-section">
              <h3>Work Experience</h3>
              <pre className="resume-pre">{form.experience}</pre>
            </div>
          )}

          {form.education && (
            <div className="resume-section">
              <h3>Education</h3>
              <pre className="resume-pre">{form.education}</pre>
            </div>
          )}

          {form.certifications && (
            <div className="resume-section">
              <h3>Certifications</h3>
              <pre className="resume-pre">{form.certifications}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
