import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Dashboard from "../components/Dashboard";

export default function Results() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const results = state?.results || [];
  const session = state?.session;
  if (!results.length) return (
    <main style={{maxWidth:440,margin:"80px auto",textAlign:"center",display:"flex",flexDirection:"column",alignItems:"center",gap:16}}>
      <div style={{fontSize:"3.5rem"}}>📊</div>
      <h2 style={{fontWeight:700,fontSize:"1.4rem",color:"var(--slate-800)"}}>No results yet</h2>
      <p style={{color:"var(--slate-500)",lineHeight:1.6}}>Complete a mock interview to see your performance analytics.</p>
      <button className="btn-primary" onClick={()=>navigate("/")}>← Start an Interview</button>
    </main>
  );
  const scores = results.map(r=>r.evaluation?.normalized_score??0);
  const avg = scores.reduce((a,b)=>a+b,0)/scores.length;
  const grade = avg>=80?"A":avg>=65?"B":avg>=45?"C":avg>=30?"D":"F";
  return (
    <main style={{maxWidth:860,margin:"0 auto",padding:"40px 24px 80px",display:"flex",flexDirection:"column",gap:28}}>
      <header style={{display:"flex",justifyContent:"space-between",alignItems:"center",background:"var(--white)",border:"1px solid var(--border-soft)",borderRadius:"var(--radius-xl)",padding:"28px 32px",boxShadow:"var(--shadow-md)"}} className="fade-up">
        <div>
          <p style={{fontSize:"0.78rem",fontWeight:600,color:"var(--blue-500)",textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:6}}>Interview complete</p>
          <h1 style={{fontSize:"1.8rem",fontWeight:800,color:"var(--slate-900)",letterSpacing:"-0.03em"}}>Your Results</h1>
          {session&&<p style={{fontSize:"0.85rem",color:"var(--slate-400)",marginTop:6}}>{session.topic} · {session.difficulty} · {results.length} questions</p>}
        </div>
        <div style={{display:"flex",flexDirection:"column",alignItems:"center",gap:4}}>
          <div style={{display:"flex",alignItems:"baseline",gap:2}}>
            <span style={{fontSize:"3rem",fontWeight:900,color:"var(--blue-600)",fontFamily:"var(--font-mono)",lineHeight:1}}>{avg.toFixed(1)}</span>
            <span style={{fontSize:"1.2rem",fontWeight:700,color:"var(--blue-400)"}}>%</span>
          </div>
          <div style={{fontSize:"0.82rem",fontWeight:700,color:"var(--blue-600)",background:"var(--blue-50)",padding:"3px 14px",borderRadius:99,letterSpacing:"0.06em"}}>Grade {grade}</div>
        </div>
      </header>
      <div className="fade-up fade-up-1"><Dashboard results={results}/></div>
      <div style={{display:"flex",justifyContent:"flex-end",gap:12}} className="fade-up fade-up-2">
        <button className="btn-ghost" onClick={()=>navigate("/")}>← New Interview</button>
        <button className="btn-primary" onClick={()=>window.print()}>🖨 Save Report</button>
      </div>
    </main>
  );
}
