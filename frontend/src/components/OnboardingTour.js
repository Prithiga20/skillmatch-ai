import { useState } from "react";

const STEPS = {
  seeker: [
    { title: "Welcome to SkillMatch AI! 👋", desc: "Your smart job matching platform. Let's take a quick tour." },
    { title: "Upload Your Resume 📄", desc: "Go to Dashboard → Upload Resume. Our AI will extract your skills automatically." },
    { title: "Get AI Job Matches 🤖", desc: "After uploading, you'll see jobs ranked by match score based on your skills." },
    { title: "Skill Gap Analysis 📊", desc: "Use Skill Gap page to see what skills you're missing for any job, with course recommendations." },
    { title: "Interview Prep 🎯", desc: "Practice interview questions tailored to your skills before applying." },
    { title: "You're all set! 🚀", desc: "Start by uploading your resume and exploring job recommendations." },
  ],
  recruiter: [
    { title: "Welcome to SkillMatch AI! 👋", desc: "Your smart recruitment platform. Let's take a quick tour." },
    { title: "Post a Job 📝", desc: "Go to Dashboard → Post a New Job. Add required skills to enable AI matching." },
    { title: "AI Candidate Matching 🤖", desc: "Click 'View AI Candidates' on any job to see ranked candidates by match score." },
    { title: "Manage Applications 📋", desc: "Review applications and update status to Shortlisted or Rejected." },
    { title: "Company Profile 🏢", desc: "Set up your company profile to attract better candidates." },
    { title: "You're all set! 🚀", desc: "Start by posting your first job and let AI find the best candidates." },
  ],
  admin: [
    { title: "Welcome Admin! 👋", desc: "You have full control over the platform." },
    { title: "Monitor Stats 📊", desc: "View total users, jobs, and applications in the Stats tab." },
    { title: "Manage Users 👥", desc: "View and delete users from the Users tab." },
    { title: "Manage Jobs 💼", desc: "View and remove job postings from the Jobs tab." },
    { title: "You're all set! 🚀", desc: "Monitor the platform and keep everything running smoothly." },
  ],
};

export default function OnboardingTour({ role, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = STEPS[role] || STEPS.seeker;

  const next = () => {
    if (step < steps.length - 1) setStep(step + 1);
    else onComplete();
  };

  const skip = () => onComplete();

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-card">
        <div className="onboarding-steps">
          {steps.map((_, i) => (
            <div key={i} className={`onboarding-dot ${i === step ? "active" : i < step ? "done" : ""}`} />
          ))}
        </div>
        <h2>{steps[step].title}</h2>
        <p>{steps[step].desc}</p>
        <div className="onboarding-actions">
          <button className="btn-link" onClick={skip}>Skip Tour</button>
          <button className="btn-primary" onClick={next}>
            {step === steps.length - 1 ? "Get Started 🚀" : "Next →"}
          </button>
        </div>
      </div>
    </div>
  );
}
