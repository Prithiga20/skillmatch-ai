import { useState, useEffect } from "react";
import api from "../api";

export default function InterviewPrep() {
  const [data, setData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/enhance/interview-prep")
      .then(({ data }) => setData(data))
      .catch((err) => setError(err.response?.data?.error || "Upload your resume first to get personalized questions."));
  }, []);

  return (
    <div className="dashboard">
      <h2>Interview Preparation</h2>

      {error && (
        <div className="dashboard-section">
          <p className="error">{error}</p>
        </div>
      )}

      {data && (
        <>
          {data.skills_covered.length > 0 && (
            <div className="dashboard-section">
              <h3>Questions based on your skills</h3>
              <div className="skill-tags">
                {data.skills_covered.map((s) => <span key={s} className="skill-tag green">{s}</span>)}
              </div>
            </div>
          )}

          <div className="dashboard-section">
            <h3>Practice Questions ({data.questions.length})</h3>
            <div className="question-list">
              {data.questions.map((q, i) => (
                <div key={i} className="question-card">
                  <p className="question-text"><strong>Q{i + 1}.</strong> {q}</p>
                  <textarea
                    placeholder="Type your answer here to practice..."
                    value={answers[i] || ""}
                    onChange={(e) => setAnswers({ ...answers, [i]: e.target.value })}
                    rows={3}
                  />
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
