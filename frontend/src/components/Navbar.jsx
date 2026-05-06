import React from "react";
import { Link, useLocation } from "react-router-dom";

const NAV_LINKS = [{ label: "Home", path: "/" }, { label: "Interview", path: "/interview" }, { label: "Results", path: "/results" }];

export default function Navbar() {
  const { pathname } = useLocation();
  return (
    <header style={S.header}>
      <nav style={S.nav}>
        <Link to="/" style={S.brand}><span style={S.brandIcon}>⬡</span><span style={S.brandName}>InterviewIQ</span></Link>
        <div style={S.links}>
          {NAV_LINKS.map(({ label, path }) => {
            const active = pathname === path;
            return (
              <Link key={path} to={path} style={{ ...S.link, ...(active ? S.linkActive : {}) }}>
                {label}{active && <span style={S.dot} />}
              </Link>
            );
          })}
        </div>
        <Link to="/" style={S.cta}>Get Started</Link>
      </nav>
    </header>
  );
}

const S = {
  header: { position:"sticky", top:0, zIndex:100, background:"rgba(255,255,255,0.88)", backdropFilter:"blur(12px)", borderBottom:"1px solid var(--border-soft)", boxShadow:"0 1px 0 rgba(15,23,42,0.04)" },
  nav: { maxWidth:1100, margin:"0 auto", padding:"0 28px", height:62, display:"flex", alignItems:"center", gap:32 },
  brand: { display:"flex", alignItems:"center", gap:9, textDecoration:"none", marginRight:"auto" },
  brandIcon: { fontSize:"1.4rem", color:"var(--blue-600)", lineHeight:1 },
  brandName: { fontSize:"1.05rem", fontWeight:700, color:"var(--slate-900)", letterSpacing:"-0.02em" },
  links: { display:"flex", gap:4 },
  link: { position:"relative", padding:"6px 14px", borderRadius:"var(--radius-sm)", fontSize:"0.875rem", fontWeight:500, color:"var(--slate-500)", textDecoration:"none", transition:"color var(--transition),background var(--transition)", display:"flex", flexDirection:"column", alignItems:"center", gap:2 },
  linkActive: { color:"var(--blue-600)", background:"var(--blue-50)", fontWeight:600 },
  dot: { width:4, height:4, borderRadius:"50%", background:"var(--blue-500)" },
  cta: { padding:"8px 20px", background:"var(--blue-600)", color:"#fff", borderRadius:"var(--radius-md)", fontSize:"0.85rem", fontWeight:600, textDecoration:"none" },
};
