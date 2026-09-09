export type LifecycleJob = {
  client: string; provider: string; status: string; service_deadline: number;
  provider_completion_checkpoint: number; client_response_checkpoint: number;
};
export type WalletRole = "CLIENT" | "PROVIDER" | "OBSERVER" | "DISCONNECTED";
export type StepState = "complete" | "available" | "locked";
export type LifecycleStep = { key: string; label: string; detail: string; state: StepState };

const progressedTo = (status: string, states: string[]) => states.includes(status);

export function walletRole(wallet: string, job: LifecycleJob | null): WalletRole {
  if (!wallet) return "DISCONNECTED";
  if (!job) return "OBSERVER";
  const normalized = wallet.toLowerCase();
  if (normalized === job.client.toLowerCase()) return "CLIENT";
  if (normalized === job.provider.toLowerCase()) return "PROVIDER";
  return "OBSERVER";
}

export function lifecycleSteps(job: LifecycleJob | null, wallet: string): LifecycleStep[] {
  const role = walletRole(wallet, job);
  const status = job?.status || "NONE";
  const scheduled = Boolean(job?.service_deadline);
  const completion = Boolean(job?.provider_completion_checkpoint);
  const response = Boolean(job?.client_response_checkpoint);
  const closed = status === "SETTLED";
  const available = (condition: boolean): StepState => condition ? "available" : "locked";
  return [
    { key: "create", label: "Create job", detail: job ? "Job is anchored on-chain." : role === "DISCONNECTED" ? "Connect a client wallet to begin." : "Lock parties, fee and immutable terms.", state: job ? "complete" : available(role !== "DISCONNECTED") },
    { key: "schedule", label: "Lock schedule", detail: scheduled ? "Three deadlines are fixed." : "Client sets service, challenge and recovery deadlines.", state: scheduled ? "complete" : available(status === "JOB_OPEN" && role === "CLIENT") },
    { key: "accept", label: "Provider accepts", detail: status === "JOB_OPEN" ? "Provider posts a 0.001 GEN bond." : "Provider bond is held by the contract.", state: progressedTo(status, ["PROVIDER_ACCEPTED", "CHECKPOINTS_ACTIVE", "DISPUTED", "ADJUDICATED", "RECOVERY", "SETTLED"]) ? "complete" : available(status === "JOB_OPEN" && scheduled && role === "PROVIDER") },
    { key: "fund", label: "Client funds", detail: status === "PROVIDER_ACCEPTED" ? "Client locks the exact job fee." : "Service fee is in custody.", state: progressedTo(status, ["CHECKPOINTS_ACTIVE", "DISPUTED", "ADJUDICATED", "RECOVERY", "SETTLED"]) ? "complete" : available(status === "PROVIDER_ACCEPTED" && role === "CLIENT") },
    { key: "completion", label: "Provider proves completion", detail: completion ? "Completion checkpoint is bound." : "Append immutable completion evidence.", state: completion ? "complete" : available(status === "CHECKPOINTS_ACTIVE" && role === "PROVIDER") },
    { key: "response", label: "Client responds", detail: response ? "Client response is bound." : "Accept, dispute or cancel with evidence.", state: response ? "complete" : available(status === "CHECKPOINTS_ACTIVE" && completion && role === "CLIENT") },
    { key: "resolve", label: "Resolve escrow", detail: closed ? `Terminal verdict: ${job?.status}.` : status === "DISPUTED" ? "Run the jury, then settle." : "Confirm completion or open a dispute.", state: closed ? "complete" : available((status === "CHECKPOINTS_ACTIVE" && completion && role === "CLIENT") || ["DISPUTED", "ADJUDICATED", "RECOVERY"].includes(status)) },
  ];
}
