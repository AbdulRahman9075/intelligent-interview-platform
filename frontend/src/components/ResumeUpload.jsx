import React, { useState, useRef, useCallback } from "react";
import { uploadResume } from "../services/api";

export default function ResumeUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const validate = (f) => {
    if (!["application/pdf","text/plain"].includes(f.type)) return "Only PDF or plain-text (.txt) files accepted.";
    if (f.size > 10*1024*1024) return "File must be smaller than 10 MB.";
    return null;
  };

  const pick = (f) => { const err = validate(f); if (err) { setError(err); return; } setError(""); setFile(f); };
  const onDrop = useCallback((e) => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) pick(f); }, []);

  const submit = async () => {
    if (!file) return;
    setLoading(true); setError("");
    try { const data = await uploadResume(file); onUploadSuccess(data); }
    catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div style={{display:"flex",flexDirection:"column",gap:16}} className="fade-up">
      <div
        style={{border:`2px dashed ${dragging?"var(--blue-400)":file?"var(--blue-300)":"var(--border)"}`,borderStyle:file?"solid":"dashed",borderRadius:"var(--radius-lg)",background:dragging||file?"var(--blue-50)":"var(--off-white)",padding:"36px 24px",cursor:file?"default":"pointer",minHeight:160,display:"flex",alignItems:"center",justifyContent:"center",transition:"all var(--transition)"}}
        onDragOver={(e)=>{e.preventDefault();setDragging(true);}} onDragLeave={()=>setDragging(false)} onDrop={onDrop}
        onClick={()=>!file&&inputRef.current?.click()}
      >
        <input ref={inputRef} type="file" accept=".pdf,.txt" style={{display:"none"}} onChange={(e)=>e.target.files[0]&&pick(e.target.files[0])} />
        {file ? (
          <div style={{display:"flex",alignItems:"center",gap:14,width:"100%",padding:"0 8px"}}>
            <span style={{fontSize:"2rem"}}>{file.type==="application/pdf"?"📄":"📝"}</span>
            <div style={{flex:1,minWidth:0}}>
              <p style={{fontWeight:600,color:"var(--slate-800)",fontSize:"0.9rem",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{file.name}</p>
              <p style={{fontSize:"0.78rem",color:"var(--slate-400)",marginTop:2}}>{file.type==="application/pdf"?"PDF":"Text"} · {(file.size/1024).toFixed(1)} KB</p>
            </div>
            <button style={{background:"none",border:"none",color:"var(--slate-400)",fontSize:"1rem",cursor:"pointer",padding:4}} onClick={(e)=>{e.stopPropagation();setFile(null);setError("");}}>✕</button>
          </div>
        ) : (
          <div style={{textAlign:"center"}}>
            <div style={{width:56,height:56,borderRadius:"var(--radius-md)",background:"var(--blue-100)",display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 14px"}}>
              <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="var(--blue-500)" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/></svg>
            </div>
            <p style={{fontWeight:600,color:"var(--slate-700)",fontSize:"0.95rem"}}>{dragging?"Drop it here!":"Drag & drop your resume"}</p>
            <p style={{fontSize:"0.8rem",color:"var(--slate-400)",margin:"4px 0 16px"}}>PDF or TXT · up to 10 MB</p>
            <button style={{padding:"8px 20px",border:"1.5px solid var(--blue-400)",borderRadius:"var(--radius-md)",background:"transparent",color:"var(--blue-600)",fontSize:"0.85rem",fontWeight:600,cursor:"pointer"}} onClick={(e)=>{e.stopPropagation();inputRef.current?.click();}}>Browse files</button>
          </div>
        )}
      </div>
      {error && <div style={{background:"var(--red-100)",color:"#991b1b",borderRadius:"var(--radius-sm)",padding:"10px 14px",fontSize:"0.85rem",fontWeight:500}}>⚠ {error}</div>}
      <button className="btn-primary" style={{width:"100%",justifyContent:"center"}} disabled={!file||loading} onClick={submit}>
        {loading ? <><div className="spinner"/>Analysing resume…</> : <><span>↑</span> Upload & Extract Skills</>}
      </button>
    </div>
  );
}
