import { createClient } from "genlayer-js";
import { localnet, studionet, testnetBradbury } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

type NetworkName = "localnet" | "studionet" | "testnetBradbury";
declare global { interface Window { ethereum?: { request: (args: { method: string; params?: unknown[] }) => Promise<unknown> } } }

const network = (process.env.NEXT_PUBLIC_NETWORK as NetworkName) || "studionet";
const endpoint = process.env.NEXT_PUBLIC_GENLAYER_RPC;
const chains = { localnet, studionet, testnetBradbury };
const readClient = createClient({ chain: chains[network] ?? studionet, ...(endpoint ? { endpoint } : {}) });
const storageKey = "cleancheckpoint.contract";

type RuntimeClient = {
  connect?: (name: NetworkName) => Promise<unknown>;
  readContract: (args: { address: string; functionName: string; args: unknown[] }) => Promise<unknown>;
  writeContract: (args: { address: string; functionName: string; args: unknown[]; value: bigint }) => Promise<string | { txId: string }>;
  waitForTransactionReceipt: (args: { hash: `0x${string}`; status: string; interval?: number; retries?: number }) => Promise<Record<string, unknown>>;
  getTransaction: (args: { hash: `0x${string}` }) => Promise<Record<string, unknown>>;
};

export type ContractResult = { success: boolean; pending?: boolean; data?: unknown; hash?: string; status?: string; error?: string };
export const address = () => typeof window !== "undefined" && localStorage.getItem(storageKey) || process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";
export const setAddress = (value: string) => localStorage.setItem(storageKey, value.trim());
export const explorerUrl = () => `${process.env.NEXT_PUBLIC_EXPLORER_BASE || "https://explorer-studio.genlayer.com/address/"}${address()}`;

export async function connectWallet(): Promise<ContractResult> {
  if (!window.ethereum) return { success: false, error: "Install or unlock an EVM wallet first." };
  try {
    const accounts = await window.ethereum.request({ method: "eth_requestAccounts" }) as string[];
    return accounts[0] ? { success: true, data: accounts[0] } : { success: false, error: "No account selected." };
  } catch (error) { return { success: false, error: error instanceof Error ? error.message : "Wallet connection failed." }; }
}

export async function readContract(functionName: string, args: unknown[] = []): Promise<ContractResult> {
  if (!address() || address().endsWith("0000000000000000000000000000000000000000")) return { success: false, error: "Configure a deployed contract address first." };
  try { return { success: true, data: await (readClient as unknown as RuntimeClient).readContract({ address: address(), functionName, args }) }; }
  catch (error) { return { success: false, error: error instanceof Error ? error.message : "Contract read failed." }; }
}

export async function writeContract(functionName: string, args: unknown[] = [], value = BigInt(0)): Promise<ContractResult> {
  if (!window.ethereum) return { success: false, error: "Connect a wallet before writing." };
  if (!address() || address().endsWith("0000000000000000000000000000000000000000")) return { success: false, error: "Configure a deployed contract address first." };
  let hash = "";
  try {
    const accounts = await window.ethereum.request({ method: "eth_requestAccounts" }) as string[];
    if (!accounts[0]) return { success: false, error: "No wallet account selected." };
    const client = createClient({ chain: chains[network] ?? studionet, ...(endpoint ? { endpoint } : {}), provider: window.ethereum, account: accounts[0] as `0x${string}` }) as unknown as RuntimeClient;
    if (client.connect) await client.connect(network);
    const raw = await client.writeContract({ address: address(), functionName, args, value });
    hash = typeof raw === "string" ? raw : raw.txId;
    const receipt = await client.waitForTransactionReceipt({ hash: hash as `0x${string}`, status: TransactionStatus.ACCEPTED, interval: 2000, retries: 100 });
    let observed = receipt;
    try { observed = await client.getTransaction({ hash: hash as `0x${string}` }); } catch { /* receipt remains authoritative */ }
    const execution = String(observed.txExecutionResultName || receipt.txExecutionResultName || "");
    if (["FINISHED_WITH_ERROR", "FAILED"].includes(execution)) return { success: false, hash, error: "Contract rejected this action." };
    return { success: true, hash, status: String(observed.statusName || receipt.statusName || "ACCEPTED"), data: receipt };
  } catch (error) { return { success: false, hash, error: error instanceof Error ? error.message : "Contract write failed." }; }
}

export function unwrap<T>(value: unknown): T | null {
  try {
    if (typeof value === "string") return JSON.parse(value) as T;
    if (value && typeof value === "object" && "result" in value) return unwrap<T>((value as { result: unknown }).result);
    return value as T;
  } catch { return null; }
}
