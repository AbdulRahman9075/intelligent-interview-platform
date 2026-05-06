import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import ResumeUpload from "../components/ResumeUpload";
import { generateQuestions } from "../services/api";

const DIFFICULTIES = ["easy","medium","hard"];

export default function Home() {
  const navigate = useNavigate();
  const [resumeData, setResumeData] = useState(null);
  const [difficulty, setDifficulty] = useState("medium");
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState("");

  const startInterview = async () => {
    if (!resumeData) return;
    setGenerating(true); setGenError("");
    try {
      const session = await generateQuestions({ resumeId: resumeData.resume_id, difficulty, numQuestions: 5 });
      navigate("/interview", { state: { session, resumeData } });
    } catch (e) { setGenError(e.message); }
    finally { setGenerating(false); }
  };

  return (
    <main style={{maxWidth:760,margin:"0 auto",padding:"48px 24px 80px"}}>
      <section style={{textAlign:"center",marginBottom:48}} className="fade-up">
        <div className="badge badge-blue" style={{marginBottom:20,display:"inline-flex"}}>AI-Powered · Adaptive · Free</div>
        <h1 style={{fontSize:"clamp(2rem,5vw,3rem)",fontWeight:700,letterSpacing:"-0.03em",lineHeight:1.18,color:"var(--slate-900)",marginBottom:18}}>
          Ace your next<br/><span style={{background:"linear-gradient(135deg,var(--blue-600),var(--blue-400))",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>technical interview</span>
        </h1>
        <p style={{fontSize:"1.05rem",color:"var(--slate-500)",maxWidth:500,margin:"0 auto 32px",lineHeight:1.7}}>Upload your resume. Our AI extracts your skills, generates personalised questions, and coaches you with instant feedback.</p>
        <div style={{display:"flex",justifyContent:"center",gap:40}}>
          {[["5+","Topics covered"],["Real-time","AI feedback"],["100%","CPU friendly"]].map(([v,l])=>(
            <div key={l} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:2}}>
              <span style={{fontWeight:700,fontSize:"1.2rem",color:"var(--blue-600)"}}>{v}</span>
              <span style={{fontSize:"0.78rem",color:"var(--slate-400)",fontWeight:500}}>{l}</span>
            </div>
          ))}
        </div>
      </section>
      <div style={{display:"flex",flexDirection:"column",gap:20}}>
        <div className="card fade-up fade-up-1" style={{padding:"28px 28px 24px"}}>
          <div style={{display:"flex",alignItems:"center",gap:14,marginBottom:22}}>
            <div style={{width:42,height:42,borderRadius:"var(--radius-md)",background:"var(--blue-50)",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="var(--blue-600)" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/></svg>
            </div>
            <div><h2 style={{fontWeight:700,fontSize:"1rem",color:"var(--slate-800)"}}>Upload Resume</h2><p style={{fontSize:"0.82rem",color:"var(--slate-400)",marginTop:2}}>PDF or plain text · AI skill extraction</p></div>
          </div>
          <ResumeUpload onUploadSuccess={setResumeData}/>
        </div>
        {resumeData&&(
          <div className="card fade-up fade-up-2" style={{padding:"28px 28px 24px"}}>
            <div style={{display:"flex",alignItems:"center",gap:14,marginBottom:22}}>
              <div style={{width:42,height:42,borderRadius:"var(--radius-md)",background:"var(--green-100)",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>
                <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#16a34a" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
              </div>
              <div><h2 style={{fontWeight:700,fontSize:"1rem",color:"var(--slate-800)"}}>Skills Detected</h2><p style={{fontSize:"0.82rem",color:"var(--slate-400)",marginTop:2}}>{resumeData.skill_count} skills found in your resume</p></div>
            </div>
            <div style={{display:"flex",flexWrap:"wrap",gap:8}}>
              {resumeData.extracted_skills.length>0?resumeData.extracted_skills.map(s=><span key={s} className="badge badge-blue" style={{fontSize:"0.75rem"}}>{s}</span>):<p style={{color:"var(--slate-400)",fontSize:"0.875rem"}}>No skills detected. Try a more detailed resume.</p>}
            </div>
          </div>
        )}
        {resumeData&&(
          <div className="card fade-up fade-up-3" style={{padding:"28px 28px 24px"}}>
            <div style={{display:"flex",alignItems:"center",gap:14,marginBottom:22}}>
              <div style={{width:42,height:42,borderRadius:"var(--radius-md)",background:"var(--amber-100)",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>
                <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#d97706" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/></svg>
              </div>
              <div><h2 style={{fontWeight:700,fontSize:"1rem",color:"var(--slate-800)"}}>Configure Interview</h2><p style={{fontSize:"0.82rem",color:"var(--slate-400)",marginTop:2}}>Choose your challenge level</p></div>
            </div>
            <div style={{display:"flex",gap:12,marginBottom:20}}>
              {DIFFICULTIES.map(d=>(
                <button key={d} style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",gap:6,padding:"14px 8px",border:`1.5px solid ${difficulty===d?"var(--blue-500)":"var(--border)"}`,borderRadius:"var(--radius-md)",background:difficulty===d?"var(--blue-50)":"var(--off-white)",cursor:"pointer",transition:"all var(--transition)"}} onClick={()=>setDifficulty(d)}>
                  <span style={{fontSize:"1.5rem"}}>{d==="easy"?"🌱":d==="medium"?"⚡":"🔥"}</span>
                  <span style={{fontSize:"0.82rem",fontWeight:600,color:"var(--slate-600)"}}>{d.charAt(0).toUpperCase()+d.slice(1)}</span>
                </button>
              ))}
            </div>
            {genError&&<div style={{background:"var(--red-100)",color:"#991b1b",borderRadius:"var(--radius-sm)",padding:"10px 14px",fontSize:"0.85rem",marginBottom:12}}>⚠ {genError}</div>}
            <button className="btn-primary" style={{width:"100%",justifyContent:"center"}} disabled={generating} onClick={startInterview}>
              {generating?<><div className="spinner"/>Generating questions…</>:<><span>▶</span> Start Mock Interview</>}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
