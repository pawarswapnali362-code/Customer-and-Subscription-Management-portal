"use client";

import { useState } from "react";
import { ArrowRight, Eye, EyeOff, KeyRound, Layers3, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { getApiBase } from "@/lib/api";

export default function LoginPage() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const response = await fetch(`${getApiBase()}/api/auth/login`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: userId, password }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Unable to sign in.");
      router.push("/dashboard");
    } catch (reason) { setError(reason instanceof TypeError ? `Cannot reach the API at ${getApiBase()}. Start the FastAPI server and try again.` : reason instanceof Error ? reason.message : "Unable to sign in."); }
    finally { setBusy(false); }
  }
  return <main className="login-screen"><div className="login-decoration"><div className="login-brand"><span className="brand-mark"><Layers3 size={18}/></span> cliently</div><div className="login-promo"><div className="promo-tag"><span></span> CUSTOMER OPERATIONS, SIMPLIFIED</div><h1>One portal.<br/><em>Every relationship.</em></h1><p>Bring customers, products, payments and support together in one clear view.</p><div className="promo-stats"><div><b>360°</b><span>customer view</span></div><i></i><div><b>One</b><span>source of truth</span></div></div></div><div className="login-decoration-foot"><span>Built for teams that care.</span><span>© 2026 Cliently</span></div><div className="glow-orb"></div></div><div className="login-form-area"><div className="login-card"><div className="mobile-brand"><span className="brand-mark"><Layers3 size={18}/></span> cliently</div><div className="login-icon"><ShieldCheck size={22}/></div><div className="eyebrow">ADMIN WORKSPACE</div><h2>Welcome back</h2><p className="login-subtitle">Sign in to manage your customer ecosystem.</p>{error&&<div className="login-error" role="alert">{error}</div>}<form onSubmit={submit}><label htmlFor="user_id">User ID</label><div className="login-input"><Mail size={17}/><input id="user_id" name="user_id" autoComplete="username" placeholder="Enter your user ID" value={userId} onChange={e=>setUserId(e.target.value)} required/></div><label htmlFor="password">Password</label><div className="login-input"><KeyRound size={17}/><input id="password" name="password" type={showPassword?"text":"password"} autoComplete="current-password" placeholder="Enter your password" value={password} onChange={e=>setPassword(e.target.value)} required/><button type="button" className="password-toggle" aria-label={showPassword?"Hide password":"Show password"} onClick={()=>setShowPassword(!showPassword)}>{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></div><button className="sign-in-button" disabled={busy}>{busy?"Signing in…":"Sign in"}<ArrowRight size={17}/></button></form><div className="demo-login"><LockKeyhole size={15}/><span><b>Demo access</b><br/>User ID <strong>admin</strong> · Password <strong>admin</strong></span></div><div className="secure-note"><span></span> Secure administrator access</div></div><div className="login-mobile-foot">© 2026 Cliently, Inc. <span>Privacy · Terms</span></div></div></main>;
}
