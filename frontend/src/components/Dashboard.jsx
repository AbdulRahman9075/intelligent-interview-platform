import React from "react";

const GRADE = { A:{color:"#166534",bg:"var(--green-100)",label:"Excellent"}, B:{color:"#1e40af",bg:"var(--blue-100)",label:"Good"}, C:{color:"#92400e",bg:"var(--amber-100)",label:"Partial"}, D:{color:"#c2410c",bg:"#ffedd5",label:"Weak"}, F:{color:"#991b1b",bg:"var(--red-100)",label:"Poor"} };
const gradeOf = s => s>=80?"A":s>=65?"B":s>=45?"C":s>=30?"D":"F";

export default function Dashboard({ results }) {
  if (!results?.length) return null;
  const scores = results.map(r=>r.evaluation?.normalized_score??0);
  const avg = scores.reduce((a,b)=>a+b,0)/scores.length;
  const g = gradeOf(avg); const gm = GRADE[g];
  const allWeak = results.flatMap(r=>r.evaluation?.weak_areas??[]);
  const weakMap = {}; allWeak.forEach(w=>{weakMap[w]=(weakMap[w]||0)+1;});
  const weakTopics = Object.entries(weakMap).sort((a,b)=>b[1]-a[1]);

  return (
    <div style={{display:"flex",flexDirection:"column",gap:20}}>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:14}}>
        {[["Overall Score",`${avg.toFixed(1)}%`,gm.label,"var(--blue-600)","var(--blue-50)"],["Best Answer",`${Math.max(...scores).toFixed(1)}%`,"Top performance","#16a34a","var(--green-100)"],["Needs Work",`${Math.min(...scores).toFixed(1)}%`,"Lowest score","#d97706","var(--amber-100)"]].map(([label,value,sub,accent,bg])=>(
          <div key={label} style={{borderRadius:"var(--radius-lg)",padding:"22px 18px",display:"flex",flexDirection:"column",alignItems:"center",gap:4,background:bg,border:"1px solid var(--border-soft)"}}>
            <span style={{fontSize:"1.9rem",fontWeight:800,letterSpacing:"-0.03em",lineHeight:1,color:accent}}>{value}</span>
            <span style={{fontSize:"0.78rem",fontWeight:600,color:accent}}>{sub}</span>
            <span style={{fontSize:"0.72rem",color:"var(--slate-400)",fontWeight:500}}>{label}</span>
          </div>
        ))}
        <div style={{borderRadius:"var(--radius-lg)",padding:"22px 18px",display:"flex",flexDirection:"column",alignItems:"center",gap:4,background:gm.bg,border:"1px solid var(--border-soft)"}}>
          <span style={{fontSize:"2.4rem",fontWeight:800,letterSpacing:"-0.03em",lineHeight:1,color:gm.color}}>{g}</span>
          <span style={{fontSize:"0.78rem",fontWeight:600,color:gm.color}}>{gm.label}</span>
          <span style={{fontSize:"0.72rem",color:gm.color,fontWeight:500}}>Overall Grade</span>
        </div>
      </div>
      <div className="card" style={{padding:24}}>
        <h3 style={{fontWeight:700,fontSize:"0.95rem",color:"var(--slate-700)",marginBottom:18}}>Score Breakdown</h3>
        <div style={{display:"flex",gap:10,alignItems:"flex-end",height:140}}>
          {results.map((r,i)=>{const s=r.evaluation?.normalized_score??0;const gm2=GRADE[gradeOf(s)];return(
            <div key={i} style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",gap:4}}>
              <div style={{flex:1,width:"100%",background:"var(--surface)",borderRadius:"var(--radius-sm)",display:"flex",alignItems:"flex-end",overflow:"hidden"}}>
                <div style={{width:"100%",height:`${Math.max(s,4)}%`,background:gm2.color,opacity:0.85,borderRadius:"var(--radius-sm) var(--radius-sm) 0 0",transition:"height 0.6s ease"}}/>
              </div>
              <div style={{fontSize:"0.72rem",fontWeight:700,color:"var(--slate-600)",fontFamily:"var(--font-mono)"}}>{s.toFixed(0)}</div>
              <div style={{fontSize:"0.72rem",color:"var(--slate-400)"}}>Q{i+1}</div>
            </div>
          );})}
        </div>
      </div>
      <div className="card" style={{padding:24}}>
        <h3 style={{fontWeight:700,fontSize:"0.95rem",color:"var(--slate-700)",marginBottom:18}}>Question-by-Question</h3>
        <div style={{display:"flex",flexDirection:"column",gap:12}}>
          {results.map((r,i)=>{const s=r.evaluation?.normalized_score??0;const gm2=GRADE[gradeOf(s)];return(
            <div key={i} style={{display:"flex",alignItems:"flex-start",gap:14,padding:14,background:"var(--off-white)",borderRadius:"var(--radius-md)",border:"1px solid var(--border-soft)"}}>
              <div style={{width:36,height:36,borderRadius:"var(--radius-sm)",display:"flex",alignItems:"center",justifyContent:"center",fontWeight:800,fontSize:"0.95rem",flexShrink:0,background:gm2.bg,color:gm2.color}}>{gradeOf(s)}</div>
              <div style={{flex:1,minWidth:0}}>
                <p style={{fontWeight:600,fontSize:"0.875rem",color:"var(--slate-800)",marginBottom:4}}>{r.question?.question_text}</p>
                <p style={{fontSize:"0.8rem",color:"var(--slate-500)",lineHeight:1.5}}>{r.evaluation?.feedback}</p>
              </div>
              <div style={{fontFamily:"var(--font-mono)",fontWeight:700,fontSize:"0.9rem",color:"var(--slate-600)",flexShrink:0}}>{s.toFixed(1)}%</div>
            </div>
          );})}
        </div>
      </div>
      {weakTopics.length>0&&(
        <div className="card" style={{padding:24}}>
          <h3 style={{fontWeight:700,fontSize:"0.95rem",color:"var(--slate-700)",marginBottom:18}}>Areas to Improve</h3>
          <div style={{display:"flex",flexDirection:"column",gap:12}}>
            {weakTopics.map(([topic,count])=>(
              <div key={topic} style={{display:"flex",alignItems:"center",gap:12}}>
                <div style={{width:8,height:8,borderRadius:"50%",background:"var(--red-500)",flexShrink:0}}/>
                <div style={{minWidth:180}}><span style={{display:"block",fontWeight:600,fontSize:"0.875rem",color:"var(--slate-700)"}}>{topic}</span><span style={{fontSize:"0.75rem",color:"var(--slate-400)"}}>{count} question{count>1?"s":""} flagged</span></div>
                <div style={{flex:1,height:6,background:"var(--surface)",borderRadius:99,overflow:"hidden"}}><div style={{height:"100%",background:"var(--red-500)",borderRadius:99,opacity:0.7,width:`${(count/results.length)*100}%`,transition:"width 0.5s ease"}}/></div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
