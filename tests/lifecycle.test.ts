import assert from "node:assert/strict";
import test from "node:test";
import { lifecycleSteps, walletRole, type LifecycleJob } from "../src/lib/lifecycle.ts";

const client = "0x1111111111111111111111111111111111111111";
const provider = "0x2222222222222222222222222222222222222222";
const job = (overrides: Partial<LifecycleJob> = {}): LifecycleJob => ({ client, provider, status: "JOB_OPEN", service_deadline: 0, provider_completion_checkpoint: 0, client_response_checkpoint: 0, ...overrides });

test("wallet roles are normalized and outsiders remain observers", () => {
  assert.equal(walletRole(client.toUpperCase(), job()), "CLIENT");
  assert.equal(walletRole(provider, job()), "PROVIDER");
  assert.equal(walletRole("0x3333333333333333333333333333333333333333", job()), "OBSERVER");
  assert.equal(walletRole("", job()), "DISCONNECTED");
});
test("only provider acceptance unlocks for a scheduled provider", () => {
  const steps = lifecycleSteps(job({ service_deadline: 123 }), provider);
  assert.equal(steps.find(step => step.key === "schedule")?.state, "complete");
  assert.equal(steps.find(step => step.key === "accept")?.state, "available");
  assert.equal(steps.find(step => step.key === "fund")?.state, "locked");
});
test("client response and resolution unlock after completion evidence", () => {
  const steps = lifecycleSteps(job({ status: "CHECKPOINTS_ACTIVE", service_deadline: 123, provider_completion_checkpoint: 4 }), client);
  assert.equal(steps.find(step => step.key === "completion")?.state, "complete");
  assert.equal(steps.find(step => step.key === "response")?.state, "available");
  assert.equal(steps.find(step => step.key === "resolve")?.state, "available");
});
test("settled jobs show a fully terminal path", () => {
  const steps = lifecycleSteps(job({ status: "SETTLED", service_deadline: 123, provider_completion_checkpoint: 4, client_response_checkpoint: 5 }), client);
  assert.equal(steps.every(step => step.state === "complete"), true);
});
