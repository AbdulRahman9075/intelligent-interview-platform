import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { evaluateAnswer } from "../services/api";

export default function InterviewPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const textRef = useRef(null);
  const session = state?.session;
  const questions = session?.questions || [];
  const [idx, setIdx] = useState(0);
  const [answer, setAnswer] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [time, setTime] = useState(0);

  useEffect(() => { const id = setInterval(() => setTime(t=>t+1), 1000); return ()=>clearInterval(id); }, [idx]);
  useEffect(() => { setTime(0); setAnswer(""); textRef.current?.focus(); }, [idx]);

  if (!session) return (
    <div style={{textAlign:"center",padding:"80px 24px",display:"flex",flexDirection:"column",alignItems:"center",gap:20}}>
      <p style={{color:"var(--slate-500)",fontSize:"1.05rem"}}>No interview session found.</p>
      <button className="btn-primary" onClick={()=>navigate("/")}>← Go Home</button>
    </div>
  );

  const q = questions[idx];
  const progress = (idx / questions.length) * 100;
  const fmt = (s) => `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;
  const wordCount = answer.trim().split(/\s+/).filter(Boolean).length;

  const submit = async () => {
    if (!answer.trim()) return;
    setLoading(true); setError("");
    try {
      const evaluation = await evaluateAnswer({ questionId: q.question_id, sessionId: session.session_id, userAnswer: answer.trim() });
      const updated = [...results, { question: q, evaluation, userAnswer: answer.trim() }];
      setResults(updated);
      if (idx < questions.length - 1) { setIdx(i=>i+1); }
      else { navigate("/results", { state: { results: updated, session, resumeData: state?.resumeData } }); }
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <main style={{maxWidth:720,margin:"0 auto",padding:"36px 24px 80px",display:"flex",flexDirection:"column",gap:20}}>
      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between"}} className="fade-up">
        <div style={{display:"flex",gap:8}}><span className="badge badge-blue">{session.topic}</span><span className="badge badge-amber">{session.difficulty}</span></div>
        <div style={{display:"flex",alignItems:"center",gap:5,fontFamily:"var(--font-mono)",fontSize:"0.85rem",fontWeight:500,color:"var(--slate-500)",background:"var(--surface)",padding:"5px 12px",borderRadius:"var(--radius-sm)"}}>⏱ {fmt(time)}</div>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:8}} className="fade-up fade-up-1">
        <div style={{display:"flex",justifyContent:"space-between"}}><span style={{fontSize:"0.82rem",fontWeight:600,color:"var(--slate-600)"}}>Question {idx+1} of {questions.length}</span><span style={{fontSize:"0.82rem",color:"var(--slate-400)"}}>{Math.round(progress)}% complete</span></div>
        <div style={{height:6,background:"var(--surface)",borderRadius:99,overflow:"hidden"}}><div style={{height:"100%",background:"linear-gradient(90deg,var(--blue-500),var(--blue-400))",borderRadius:99,width:`${progress}%`,transition:"width 0.4s ease"}}/></div>
        <div style={{display:"flex",gap:6}}>{questions.map((_,i)=><div key={i} style={{width:8,height:8,borderRadius:"50%",background:i<idx?"var(--blue-400)":i===idx?"var(--blue-600)":"var(--border)",transform:i===idx?"scale(1.25)":"none",transition:"all var(--transition)"}}/>)}</div>
      </div>
      <div className="card fade-up fade-up-2" style={{padding:28}}>
        <div style={{display:"inline-block",background:"var(--blue-600)",color:"#fff",fontSize:"0.72rem",fontWeight:700,letterSpacing:"0.06em",padding:"3px 10px",borderRadius:"var(--radius-sm)",marginBottom:16,fontFamily:"var(--font-mono)"}}>Q{idx+1}</div>
        <p style={{fontSize:"1.12rem",fontWeight:600,color:"var(--slate-800)",lineHeight:1.6,letterSpacing:"-0.01em"}}>{q.question_text}</p>
        <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginTop:16}}>
          <span style={{fontSize:"0.78rem",color:"var(--slate-400)"}}>Topic: {q.topic}</span>
          <span style={{fontSize:"0.72rem",fontWeight:600,padding:"3px 10px",borderRadius:99,textTransform:"capitalize",background:q.difficulty==="easy"?"var(--green-100)":q.difficulty==="medium"?"var(--amber-100)":"var(--red-100)",color:q.difficulty==="easy"?"#166534":q.difficulty==="medium"?"#92400e":"#991b1b"}}>{q.difficulty}</span>
        </div>
      </div>
      <div className="card fade-up fade-up-3" style={{padding:22}}>
        <label style={{display:"block",fontSize:"0.82rem",fontWeight:600,color:"var(--slate-600)",marginBottom:10}}>Your Answer</label>
        <textarea ref={textRef} style={{width:"100%",border:"1.5px solid var(--border)",borderRadius:"var(--radius-md)",padding:"14px 16px",fontSize:"0.93rem",color:"var(--slate-800)",background:"var(--off-white)",resize:"vertical",outline:"none",lineHeight:1.65}} placeholder="Type your answer here. Be specific, use examples, and explain your reasoning…" value={answer} onChange={e=>setAnswer(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&(e.ctrlKey||e.metaKey))submit();}} rows={7} disabled={loading}/>
        <div style={{display:"flex",justifyContent:"space-between",marginTop:8}}><span style={{fontSize:"0.78rem",color:"var(--slate-400)",fontFamily:"var(--font-mono)"}}>{wordCount} word{wordCount!==1?"s":""}</span><span style={{fontSize:"0.78rem",color:"var(--slate-300)"}}>Ctrl+Enter to submit</span></div>
      </div>
      {error && <div style={{background:"var(--red-100)",color:"#991b1b",borderRadius:"var(--radius-sm)",padding:"10px 14px",fontSize:"0.85rem",fontWeight:500}} className="fade-up">⚠ {error}</div>}
      <div style={{display:"flex",justifyContent:"flex-end",gap:12}} className="fade-up fade-up-4">
        <button className="btn-ghost" onClick={()=>setIdx(i=>i+1)} disabled={loading||idx===questions.length-1}>Skip →</button>
        <button className="btn-primary" style={{minWidth:160}} disabled={!answer.trim()||loading} onClick={submit}>
          {loading?<><div className="spinner"/>Evaluating…</>:idx<questions.length-1?"Submit & Next →":"Finish Interview ✓"}
        </button>
      </div>
    </main>
  );
}
