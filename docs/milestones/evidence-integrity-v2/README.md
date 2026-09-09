# Evidence Integrity & Prompt Security v2

## Before

The accepted contract validated the syntax of `sha256:` declarations, then adjudication rendered the URLs directly. A changed gateway response could therefore be interpreted without proving it matched the committed bytes, and checkpoint digests could be reused.

```python
provider_evidence = gl.nondet.web.render(provider_url, mode="text")[:5000]
client_evidence = gl.nondet.web.render(client_url, mode="text")[:5000]
```

## After

Every required source is fetched as bytes and verified before the LLM sees it. Checkpoint digests are globally single-use. Explicit untrusted boundaries and a fixed `CC_V2` canary make injected output instructions fail closed.

```python
body = gl.nondet.web.get(url).body
actual = "sha256:" + hashlib.sha256(body).hexdigest()
if actual.lower() != expected.lower():
    return ""
```

## Quantified change

- 3/3 adjudication sources now receive byte-exact integrity checks (previously 0/3).
- 1 global replay index prevents checkpoint-digest reuse (previously none).
- 4 new security regressions: malformed/zero address, evidence replay, byte tamper, canary manipulation.
- Paying verdicts require both `integrity=VERIFIED` and `canary=CC_V2`.

## Verification

```bash
python -m pytest tests -p no:cacheprovider
npm run test:ui
npm run lint
npm run build
```

## Deployment status

Deployed on Studionet at `0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c`. The empty-state interface is verified; funded lifecycle, semantic dispute, tamper recovery, and zero-held conservation remain the next evidence layer.
