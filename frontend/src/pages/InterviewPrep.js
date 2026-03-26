import { useState, useEffect } from "react";
import api from "../api";

const GRADE_COLOR = { A: "#276749", B: "#2b6cb0", C: "#92400e", D: "#c05621", F: "#c53030" };
const GRADE_BG   = { A: "#e6ffed", B: "#e8f4fd", C: "#fef3c7", D: "#feebc8", F: "#fff5f5" };

export default function InterviewPrep() {
  const [availableSkills, setAvailableSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState("");
  const [questions, setQuestions]   = useState([]);
  const [skillsCovered, setSkillsCovered] = useState([]);
  const [answers, setAnswers]       = useState({});
  const [loading, setLoading]       = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults]       = useState(null);
  const [error, setError]           = useState("");
  const [step, setStep]             = useState("select"); // select | practice | results

  // Load available skills on mount
  useEffect(() => {
    api.get("/enhance/interview-prep")
      .then(({ data }) => {
        setAvailableSkills(data.available_skills || []);
        if (data.skills_covered.length > 0) {
          setSkillsCovered(data.skills_covered);
          setQuestions(data.questions);
          setSelectedSkill(data.skills_covered[0]);
        }
      })
      .catch(() => {
        // no resume — still load available skills via fallback
        setAvailableSkills(["python","machine learning","react","sql","javascript","java","aws","docker"]);
      });
  }, []);

  const loadQuestions = async () => {
    if (!selectedSkill) { setError("Please select a skill."); return; }
    setLoading(true);
    setError("");
    setAnswers({});
    setResults(null);
    try {
      const { data } = await api.get("/enhance/interview-prep", { params: { skill: selectedSkill } });
      setQuestions(data.questions);
      setSkillsCovered(data.skills_covered);
      setStep("practice");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load questions.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    const unanswered = questions.filter((_, i) => !answers[i]?.trim());
    if (unanswered.length === questions.length) { setError("Please answer at least one question."); return; }
    setSubmitting(true);
    setError("");
    try {
      const submissions = questions.map((q, i) => ({
        question: q,
        answer: answers[i] || "",
        skill: selectedSkill,
      }));
      const { data } = await api.post("/enhance/interview-evaluate", { submissions });
      setResults(data);
      setStep("results");
    } catch (err) {
      setError(err.response?.data?.error || "Evaluation failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const restart = () => {
    setStep("select");
    setAnswers({});
    setResults(null);
    setQuestions([]);
    setError("");
  };

  return (
    <div className="dashboard">
      <div className="ip-header">
        <h2>🎯 Interview Preparation</h2>
        <p className="ip-subtitle">Practice questions, submit answers, and get instant AI feedback</p>
      </div>

      {error && <div className="ip-error">{error}</div>}

      {/* STEP 1: Select Skill */}
      {step === "select" && (
        <div className="dashboard-section">
          <h3>Select a Skill to Practice</h3>
          <p style={{ color: "#666", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
            Choose a skill to get targeted technical + HR questions
          </p>

          <div className="ip-skill-grid">
            {availableSkills.map((skill) => (
              <button
                key={skill}
                className={`ip-skill-btn ${selectedSkill === skill ? "active" : ""}`}
                onClick={() => setSelectedSkill(skill)}
              >
                {SKILL_ICONS[skill] || "💡"} {skill.charAt(0).toUpperCase() + skill.slice(1)}
              </button>
            ))}
          </div>

          {skillsCovered.length > 0 && (
            <div className="ip-resume-hint">
              📄 Resume detected skills:
              {skillsCovered.map(s => <span key={s} className="skill-tag green" style={{ marginLeft: "0.4rem" }}>{s}</span>)}
            </div>
          )}

          <button
            className="btn-primary"
            style={{ marginTop: "1.5rem", padding: "0.7rem 2rem" }}
            onClick={loadQuestions}
            disabled={loading || !selectedSkill}
          >
            {loading ? "Loading..." : "Start Practice →"}
          </button>
        </div>
      )}

      {/* STEP 2: Practice */}
      {step === "practice" && (
        <>
          <div className="ip-practice-header">
            <div>
              <span className="ip-skill-badge">{selectedSkill.toUpperCase()}</span>
              <span style={{ color: "#666", fontSize: "0.9rem", marginLeft: "0.75rem" }}>
                {questions.length} questions
              </span>
            </div>
            <button className="btn-secondary" onClick={restart}>← Change Skill</button>
          </div>

          {/* HR Section */}
          <div className="dashboard-section">
            <h3>🧑‍💼 HR / Behavioural Questions</h3>
            <div className="question-list">
              {questions.slice(0, 5).map((q, i) => (
                <QuestionCard
                  key={i}
                  index={i}
                  question={q}
                  answer={answers[i] || ""}
                  onChange={(val) => setAnswers({ ...answers, [i]: val })}
                />
              ))}
            </div>
          </div>

          {/* Technical Section */}
          {questions.length > 5 && (
            <div className="dashboard-section">
              <h3>⚙️ Technical Questions — {selectedSkill.charAt(0).toUpperCase() + selectedSkill.slice(1)}</h3>
              <div className="question-list">
                {questions.slice(5).map((q, i) => (
                  <QuestionCard
                    key={i + 5}
                    index={i + 5}
                    question={q}
                    answer={answers[i + 5] || ""}
                    onChange={(val) => setAnswers({ ...answers, [i + 5]: val })}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="ip-submit-bar">
            <span style={{ color: "#666", fontSize: "0.9rem" }}>
              {Object.values(answers).filter(a => a.trim()).length} / {questions.length} answered
            </span>
            <button
              className="btn-primary"
              style={{ padding: "0.75rem 2.5rem", fontSize: "1rem" }}
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? "Evaluating..." : "Submit & Get Feedback 🚀"}
            </button>
          </div>
        </>
      )}

      {/* STEP 3: Results */}
      {step === "results" && results && (
        <>
          {/* Overall Score Card */}
          <div className="ip-score-card">
            <div className="ip-score-circle" style={{ borderColor: GRADE_COLOR[results.overall_grade] }}>
              <span className="ip-score-num" style={{ color: GRADE_COLOR[results.overall_grade] }}>
                {results.overall_score}
              </span>
              <span className="ip-score-label">/ 100</span>
            </div>
            <div className="ip-score-info">
              <h3>Overall Grade:
                <span className="ip-grade-badge" style={{ background: GRADE_BG[results.overall_grade], color: GRADE_COLOR[results.overall_grade] }}>
                  {results.overall_grade}
                </span>
              </h3>
              <p>{results.answered} of {results.total_questions} questions answered</p>
              <p style={{ marginTop: "0.5rem", color: "#555" }}>{getOverallFeedback(results.overall_score)}</p>
            </div>
          </div>

          {/* Per-question Results */}
          <div className="dashboard-section">
            <h3>📋 Detailed Feedback</h3>
            <div className="question-list">
              {results.results.map((r, i) => (
                <div key={i} className="ip-result-card">
                  <div className="ip-result-header">
                    <p className="question-text"><strong>Q{i + 1}.</strong> {r.question}</p>
                    <div className="ip-result-score" style={{ background: GRADE_BG[r.grade], color: GRADE_COLOR[r.grade] }}>
                      {r.grade} — {r.score}%
                    </div>
                  </div>
                  {answers[i] && (
                    <div className="ip-your-answer">
                      <strong>Your answer:</strong> {answers[i]}
                    </div>
                  )}
                  <div className="ip-feedback">
                    💬 {r.feedback}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="ip-submit-bar">
            <button className="btn-secondary" onClick={() => { setStep("practice"); setResults(null); }}>
              ← Revise Answers
            </button>
            <button className="btn-primary" onClick={restart}>
              Practice Another Skill 🔄
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function QuestionCard({ index, question, answer, onChange }) {
  const wordCount = answer.trim() ? answer.trim().split(/\s+/).length : 0;
  return (
    <div className="question-card">
      <p className="question-text"><strong>Q{index + 1}.</strong> {question}</p>
      <textarea
        placeholder="Type your answer here to practice... (aim for 40+ words)"
        value={answer}
        onChange={(e) => onChange(e.target.value)}
        rows={4}
      />
      <div className="ip-word-count" style={{ color: wordCount >= 40 ? "#276749" : wordCount >= 15 ? "#92400e" : "#c53030" }}>
        {wordCount} words {wordCount >= 40 ? "✓" : wordCount >= 15 ? "— try to add more" : "— too short"}
      </div>
    </div>
  );
}

function getOverallFeedback(score) {
  if (score >= 85) return "Excellent! You're well-prepared for interviews. Keep it up!";
  if (score >= 70) return "Good performance! Review the feedback and strengthen weak areas.";
  if (score >= 50) return "Fair attempt. Focus on using more keywords and elaborating your answers.";
  if (score >= 30) return "Needs improvement. Practice more and aim for detailed, structured answers.";
  return "Keep practicing! Try to answer all questions with at least 40 words each.";
}

const SKILL_ICONS = {
  python: "🐍", "machine learning": "🤖", react: "⚛️", sql: "🗄️",
  javascript: "🟨", java: "☕", aws: "☁️", docker: "🐳",
};
