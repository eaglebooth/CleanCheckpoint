"use client";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Check, ExternalLink, ShieldCheck, Sparkles, Wallet, X } from "lucide-react";
import { activeNetwork, connectWallet, explorerUrl, readContract, unwrap, writeContract } from "@/lib/genlayer";

type Job = { id: number; client: string; provider: string; title: string; service: string; fee: string; bond: string; status: string; verdict: string; service_deadline: number; challenge_deadline: number; recovery_deadline: number; provider_paid: string; provider_refunded: string; client_paid: string; client_refunded: string };
type Totals = { jobs: number; checkpoints: number; deposited: string; held: string; paid: string; refunded: string };
type Toast = { kind: "ok" | "error" | "pending"; message: string; hash?: string } | null;
const cleanError = (value: unknown) => value instanceof Error ? value.message : String(value || "Unknown error");
const wei = (value: string) => {
  const normalized = value.trim();
  if (!/^(0|[1-9]\d*)(\.\d{1,18})?$/.test(normalized)) throw new Error("Enter a positive GEN amount with at most 18 decimals.");
  const [whole, fraction = ""] = normalized.split(".");
  return BigInt(whole) * BigInt(10) ** BigInt(18) + BigInt(fraction.padEnd(18, "0"));
};
const formatGen = (value: string) => {
  const amount = BigInt(value);
  const unit = BigInt(10) ** BigInt(18);
  const whole = amount / unit;
  const fraction = (amount % unit).toString().padStart(18, "0").replace(/0+$/, "");
  return fraction ? `${whole}.${fraction} GEN` : `${whole} GEN`;
};
const sampleTermsUrl = "https://gateway.pinata.cloud/ipfs/QmQBQDCyfCNC63GBDCSP7WfTNBkTSWSRpUg4Hr7aZjAdKH";
const sampleTermsDigest = "sha256:03d4c0e4185b0a7da060a9f1efc0e29cf6e6d3cc9ae3030de56de7c754873cff";

export default function AppShell() {
  const [wallet, setWallet] = useState("");
  const [scrolled, setScrolled] = useState(false);
  const [workspace, setWorkspace] = useState(false);
  const [jobId, setJobId] = useState("0");
  const [job, setJob] = useState<Job | null>(null);
  const [toast, setToast] = useState<Toast>(null);
  const [busy, setBusy] = useState("");
  const [totals, setTotals] = useState<Totals | null>(null);
  const [showcase, setShowcase] = useState<Job[]>([]);
  const [showcaseError, setShowcaseError] = useState("");
  const [create, setCreate] = useState({ title: "Apartment reset", service: "HOME", provider: "", fee: "0.01", termsUrl: sampleTermsUrl, termsDigest: sampleTermsDigest });
  const [checkpoint, setCheckpoint] = useState({ kind: "ARRIVAL", url: "", digest: "", revision: "1" });

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 36);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    const targets = document.querySelectorAll(
      ".section h2, .service-card, .service-strip, .protocol-grid > div, .steps article, .metric-grid article, .faq details, footer .shell"
    );
    targets.forEach((target) => target.classList.add("reveal"));
    const observer = new IntersectionObserver(
      (entries) => entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      }),
      { threshold: 0.12, rootMargin: "0px 0px -48px" }
    );
    targets.forEach((target) => observer.observe(target));
    return () => {
      window.removeEventListener("scroll", onScroll);
      observer.disconnect();
    };
  }, []);
  useEffect(() => {
    async function loadPublicEvidence() {
      const totalsResult = await readContract("get_totals");
      const parsedTotals = totalsResult.success ? unwrap<Totals>(totalsResult.data) : null;
      if (!parsedTotals) {
        setShowcaseError(totalsResult.error || "The public contract snapshot is temporarily unavailable.");
        return;
      }
      setTotals(parsedTotals);
      const start = Math.max(0, parsedTotals.jobs - 5);
      const jobs = await Promise.all(Array.from({ length: parsedTotals.jobs - start }, async (_, offset) => {
        const result = await readContract("get_job", [start + offset]);
        return result.success ? unwrap<Job>(result.data) : null;
      }));
      setShowcase(jobs.filter((item): item is Job => Boolean(item && typeof item === "object")));
    }
    void loadPublicEvidence();
  }, []);
  const shortWallet = useMemo(() => wallet ? `${wallet.slice(0, 6)}…${wallet.slice(-4)}` : "Connect wallet", [wallet]);
  const notify = (kind: "ok" | "error" | "pending", message: string, hash?: string) => setToast({ kind, message, hash });

  async function connect() {
    const result = await connectWallet();
    if (result.success) { setWallet(String(result.data)); notify("ok", "Wallet connected."); }
    else notify("error", result.error || "Wallet connection failed.");
  }

  async function refresh(id = jobId, silent = false): Promise<boolean> {
    const result = await readContract("get_job", [Number(id)]);
    const parsed = result.success ? unwrap<Job>(result.data) : null;
    if (parsed && typeof parsed === "object" && parsed.id === Number(id)) {
      setJob(parsed);
      if (!silent) notify("ok", `Job #${id} read from contract.`);
      return true;
    }
    setJob(null);
    if (!silent) notify("error", result.error || "Job not found or contract is not configured.");
    return false;
  }

  async function run(label: string, fn: () => Promise<{ success: boolean; hash?: string; error?: string }>, verify = true) {
    setBusy(label); notify("pending", `${label}: waiting for contract acceptance…`);
    try {
      const result = await fn();
      if (!result.success) return notify("error", result.error || `${label} failed.`, result.hash);
      if (verify && label !== "Create job") {
        const verified = await refresh(jobId, true);
        if (!verified) {
          notify("error", `${label} was accepted, but authoritative read-back failed. Verify the transaction before continuing.`, result.hash);
          return false;
        }
      }
      if (verify) notify("ok", `${label} accepted. State was read back from the contract.`, result.hash);
      return true;
    } catch (error) { notify("error", cleanError(error)); }
    finally { setBusy(""); }
    return false;
  }

  async function createJob() {
    const connected = wallet ? { success: true, data: wallet } : await connectWallet();
    if (!connected.success) {
      notify("error", connected.error || "Connect a funded client wallet first.");
      return;
    }
    const client = String(connected.data).toLowerCase();
    setWallet(String(connected.data));
    const before = await readContract("get_totals");
    const beforeTotals = before.success ? unwrap<Totals>(before.data) : null;
    const accepted = await run("Create job", () => writeContract("create_job", [create.title, create.service, create.provider, wei(create.fee), create.termsUrl, create.termsDigest]), false);
    if (!accepted) return;
    if (!beforeTotals) {
      notify("error", "Job was accepted, but the previous job counter was unavailable, so its ID cannot be matched safely.");
      return;
    }
    const after = await readContract("get_totals");
    const afterTotals = after.success ? unwrap<Totals>(after.data) : null;
    if (!afterTotals) {
      notify("error", "Job was accepted, but the new ID could not be verified. Reload the public snapshot before continuing.");
      return;
    }
    for (let id = afterTotals.jobs - 1; id >= beforeTotals.jobs; id -= 1) {
      const candidateResult = await readContract("get_job", [id]);
      const candidate = candidateResult.success ? unwrap<Job>(candidateResult.data) : null;
      if (candidate && candidate.client === client && candidate.provider === create.provider.toLowerCase() && candidate.title === create.title) {
        setJobId(String(id));
        setJob(candidate);
        notify("ok", `Job #${id} created and verified from the contract.`);
        return;
      }
    }
    notify("error", "Job was accepted, but its ID could not be matched safely. Reload the public snapshot before continuing.");
  }

  return <main>
    <section className="hero" id="home">
      <nav className={`nav shell ${scrolled ? "nav-scrolled" : ""}`}>
        <a className="brand" href="#home"><span className="brand-mark"><Sparkles size={22}/></span><span>CleanCheckpoint</span></a>
        <div className="nav-links"><a href="#services">Services</a><a href="#evidence">Evidence</a><a href="#protocol">How it works</a><a href="#trust">Trust model</a><a href="#faq">FAQ</a></div>
        <div className="nav-actions"><a className="icon-btn" href={explorerUrl()} target="_blank" rel="noreferrer" aria-label="Open CleanCheckpoint contract in GenLayer Explorer" title="Open contract in Explorer"><ExternalLink size={19}/></a><button className="dark-btn" onClick={connect}><Wallet size={17}/>{shortWallet}</button></div>
      </nav>
      <div className="hero-image" />
      <div className="hero-overlay" />
      <div className="hero-copy shell">
        <div className="eyebrow light"><ShieldCheck size={17}/> Checkpoints, not surveillance</div>
        <h1>Cleaning work,<br/>verified fairly.</h1>
        <p>Lock service terms, record role-bound checkpoints, and release payment without trusting a single platform operator.</p>
        <div className="hero-buttons"><button className="white-btn" onClick={() => setWorkspace(true)}>Open workspace <ArrowRight size={19}/></button><a className="ghost-btn" href="#protocol">See the protocol</a></div>
      </div>
      <div className="trust-card"><strong>Exception-only jury</strong><span>Happy paths settle without AI</span><div className="trust-row"><span className="avatars">CC</span><span><b>4 bounded facts</b><small>deterministic payout</small></span></div></div>
    </section>

    <section className="section shell" id="services">
      <div className="section-kicker">● Service templates</div><h2>Designed for work that can<br/>be checkpointed clearly.</h2>
      <div className="service-card featured"><span className="service-num">01</span><div className="service-photo home"/><div className="service-copy"><h3>Home cleaning</h3><p>Arrival, work start, checklist submission and client response—without publishing private home photos.</p><button className="blue-btn" onClick={() => { setCreate({...create, service:"HOME"}); setWorkspace(true); }}>Create job <ArrowRight size={18}/></button><div className="chips"><span>Apartment</span><span>Deep clean</span><span>Recurring</span></div></div></div>
      <div className="service-strip"><span>02</span><div><h3>Office turnover</h3><p>Role-bound evidence for scheduled commercial cleaning.</p></div><div className="chips"><span>Office</span><span>Move-out</span><span>Checklist</span></div></div>
    </section>

    <section className="evidence-section section" id="evidence"><div className="shell"><div className="section-kicker">● Public contract snapshot</div><div className="evidence-head"><div><h2>Verify outcomes<br/>without connecting a wallet.</h2><p>These latest records are read directly from the deployed studionet contract. Open a job to inspect its authoritative state and settlement, when complete.</p></div>{totals && <div className="totals-card"><strong>{totals.jobs}</strong><span>on-chain jobs</span><small>{showcase.filter(item => item.status === "SETTLED").length} of the latest {showcase.length} settled · {formatGen(totals.deposited)} deposited · {formatGen(totals.held)} held</small></div>}</div>{showcaseError ? <p className="evidence-error">{showcaseError}</p> : <div className="evidence-grid">{showcase.map(item=><article key={item.id}><div><span>Job #{item.id}</span><b>{item.status}</b></div><h3>{item.title}</h3><p>{item.verdict.replaceAll("_", " ")}</p><button onClick={()=>{setJobId(String(item.id));setJob(item);setWorkspace(true)}}>Inspect state <ArrowRight size={16}/></button></article>)}</div>}</div></section>
    <section className="protocol" id="protocol"><div className="shell protocol-grid"><div><div className="section-kicker">● How it works</div><h2>Five checkpoints.<br/>One bounded outcome.</h2><p>AI never decides how clean a home looks. It only classifies disputed public records into four closed facts.</p><button className="blue-btn" onClick={() => setWorkspace(true)}>Launch workspace <ArrowRight size={18}/></button></div><div className="steps">{[["01","Lock terms","Client pins fee, provider, exact evidence authority and deadlines."],["02","Accept + fund","Provider bonds the job; client funds the exact fee."],["03","Attest","Each party appends role-bound checkpoint revisions."],["04","Resolve","Mutual completion settles directly; disputes invoke consensus."],["05","Read back","Every write is confirmed against authoritative contract state."]].map(([n,t,d])=><article key={n}><span>{n}</span><div><h3>{t}</h3><p>{d}</p></div></article>)}</div></div></section>

    <section className="section shell" id="trust"><div className="section-kicker center">● Why this primitive is different</div><h2 className="center">Consensus only where<br/>meaning is ambiguous.</h2><div className="metric-grid"><article><span className="metric-icon"><Check/></span><h3>Deterministic happy path</h3><p>Client confirmation releases fee and returns provider bond without an AI call.</p></article><article className="metric-main"><strong>4</strong><h3>Bounded jury facts</h3><p>Arrival, completion band, client response, and source conflict. No free-form payout.</p></article><article className="metric-blue"><h3>Append-only evidence</h3><p>Every revision preserves actor, role, immutable URL, digest, and predecessor.</p><button className="white-btn" onClick={() => setWorkspace(true)}>Try the flow <ArrowRight size={18}/></button></article></div></section>

    <section className="faq section" id="faq"><div className="shell"><div className="section-kicker center">● FAQ</div><h2 className="center">Transparent by design.</h2>{[["Does CleanCheckpoint judge photos?","No. The MVP deliberately avoids subjective image grading and private home imagery."],["When does GenLayer consensus run?","Only after both parties have submitted role-bound evidence and a dispute is opened."],["What if someone disappears?","Every funded state has a locked terminal deadline. Non-funding returns the provider bond; missing completion protects the client; client silence pays documented completion; stalled adjudication returns each principal."],["Is transaction finality treated as success?","No. The app inspects contract-level rollback payloads and re-reads the affected job before reporting verified success."]].map(([q,a],i)=><details key={q} open={i===0}><summary>{q}<span>+</span></summary><p>{a}</p></details>)}</div></section>

    <footer><div className="shell"><a className="brand" href="#home"><span className="brand-mark"><Sparkles size={22}/></span>CleanCheckpoint</a><p>Checkpoint-based service verification on GenLayer.</p></div></footer>

    {workspace && <div className="modal-backdrop"><div className="workspace-panel"><div className="panel-head"><div><div className="section-kicker">Contract workspace · {activeNetwork()}</div><h2>Run the real lifecycle</h2><p className="workspace-note">Use two funded wallets: client locks 0.01 GEN and provider locks a 0.001 GEN bond. Studio deployments are Explorer Preview projects.</p></div><button className="icon-btn" onClick={() => setWorkspace(false)} aria-label="Close contract workspace"><X/></button></div><div className="workspace-grid">
      <section className="form-card"><h3>Create a service job</h3><label>Job title<input value={create.title} onChange={e=>setCreate({...create,title:e.target.value})}/></label><div className="two"><label>Service<select value={create.service} onChange={e=>setCreate({...create,service:e.target.value})}><option>HOME</option><option>OFFICE</option><option>MOVE_OUT</option><option>DEEP_CLEAN</option></select></label><label>Fee (GEN)<input value={create.fee} onChange={e=>setCreate({...create,fee:e.target.value})}/></label></div><label>Provider wallet<input placeholder="0x…" value={create.provider} onChange={e=>setCreate({...create,provider:e.target.value})}/></label><label>Immutable terms URL<input placeholder="https://ipfs.io/ipfs/…" value={create.termsUrl} onChange={e=>setCreate({...create,termsUrl:e.target.value})}/></label><label>Terms SHA-256<input placeholder="sha256:…" value={create.termsDigest} onChange={e=>setCreate({...create,termsDigest:e.target.value})}/></label><button className="blue-btn full" disabled={!!busy} onClick={createJob}>Create on-chain <ArrowRight size={18}/></button></section>
      <section className="form-card"><h3>Job actions</h3><div className="lookup"><input inputMode="numeric" value={jobId} onChange={e=>{setJobId(e.target.value);setJob(null)}}/><button onClick={()=>refresh()}>Load job</button></div><div className="action-grid"><button disabled={!!busy} onClick={()=>{const now=Math.floor(Date.now()/1000);run("Lock schedule",()=>writeContract("set_schedule",[Number(jobId),now+3600,now+7200,now+10800]))}}>Lock 1h test schedule</button><button disabled={!!busy} onClick={()=>run("Accept job",()=>writeContract("accept_job",[Number(jobId)],wei("0.001")))}>Accept + bond</button><button disabled={!!busy || !job || job.id !== Number(jobId)} onClick={()=>run("Fund job",()=>writeContract("fund_job",[Number(jobId)],job ? BigInt(job.fee) : BigInt(0)))}>Fund exact fee</button><button disabled={!!busy} onClick={()=>run("Confirm completion",()=>writeContract("confirm_completion",[Number(jobId)]))}>Mutual complete</button><button disabled={!!busy} onClick={()=>run("Open dispute",()=>writeContract("open_dispute",[Number(jobId)]))}>Open dispute</button><button disabled={!!busy} onClick={()=>run("Adjudicate",()=>writeContract("adjudicate",[Number(jobId)]))}>Run jury</button><button disabled={!!busy} onClick={()=>run("Settle",()=>writeContract("settle",[Number(jobId)]))}>Settle</button><button disabled={!!busy} onClick={()=>run("Recover",()=>writeContract("recover",[Number(jobId)]))}>Recover after deadline</button></div><hr/><h3>Append checkpoint</h3><div className="two"><select value={checkpoint.kind} onChange={e=>setCheckpoint({...checkpoint,kind:e.target.value})}>{["ARRIVAL","WORK_STARTED","CHECKLIST_SUBMITTED","COMPLETION","CLIENT_RESPONSE","CANCELLATION","COMPLETION_ACK"].map(x=><option key={x}>{x}</option>)}</select><input value={checkpoint.revision} onChange={e=>setCheckpoint({...checkpoint,revision:e.target.value})} placeholder="Revision"/></div><input value={checkpoint.url} onChange={e=>setCheckpoint({...checkpoint,url:e.target.value})} placeholder="Immutable evidence URL"/><input value={checkpoint.digest} onChange={e=>setCheckpoint({...checkpoint,digest:e.target.value})} placeholder="sha256:…"/><button className="outline-btn full" disabled={!!busy} onClick={()=>run("Record checkpoint",()=>writeContract("record_checkpoint",[Number(jobId),checkpoint.kind,checkpoint.url,checkpoint.digest,Number(checkpoint.revision)]))}>Record checkpoint</button></section>
      <aside className="state-card"><div className="state-top"><span>Authoritative state</span><button onClick={()=>refresh()}>Refresh</button></div>{job ? <><div className="status-pill">{job.status}</div><h3>#{job.id} · {job.title}</h3><dl><dt>Service</dt><dd>{job.service}</dd><dt>Verdict</dt><dd>{job.verdict}</dd><dt>Fee</dt><dd>{formatGen(job.fee)}</dd><dt>Bond</dt><dd>{formatGen(job.bond)}</dd><dt>Provider earned</dt><dd>{formatGen(job.provider_paid)}</dd><dt>Provider bond returned</dt><dd>{formatGen(job.provider_refunded)}</dd><dt>Client compensation</dt><dd>{formatGen(job.client_paid)}</dd><dt>Client fee refunded</dt><dd>{formatGen(job.client_refunded)}</dd></dl><p className="mono">Client {job.client}</p><p className="mono">Provider {job.provider}</p></> : <div className="empty-state"><ShieldCheck/><p>Load a job to verify its state directly from the configured contract.</p></div>}</aside>
    </div></div></div>}

    {toast && <div className={`toast ${toast.kind}`}><button onClick={()=>setToast(null)} aria-label="Dismiss notification"><X size={15}/></button><strong>{toast.kind === "ok" ? "Verified" : toast.kind === "pending" ? "Processing" : "Action failed"}</strong><span>{toast.message}</span>{toast.hash && <small>{toast.hash.slice(0,12)}…{toast.hash.slice(-8)}</small>}{toast.hash && <a href={explorerUrl()} target="_blank" rel="noreferrer">Verify contract on Explorer <ExternalLink size={13}/></a>}</div>}
  </main>;
}
