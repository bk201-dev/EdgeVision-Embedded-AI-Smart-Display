# Validation Plan

## AI Validation

- Evaluate on a held-out test set.
- Report per-class metrics.
- Test low-light conditions.
- Test multiple camera distances.
- Test different poses.
- Record failure cases.
- Verify confidence-threshold behavior.

## Embedded Validation

- Verify communication between inference device and MCU.
- Verify malformed / missing messages are handled safely.
- Verify display changes to the correct content.
- Verify fallback content is shown when no valid classification is available.
- Verify restart / power-cycle behavior.

## End-to-End Validation

| Test | Expected Result | Status |
|---|---|---|
| Camera starts | Live frame available | ⬜ |
| Model loads | No runtime error | ⬜ |
| Valid class received | Correct content ID generated | ⬜ |
| Low confidence | Fallback content selected | ⬜ |
| MCU receives command | Correct state update | ⬜ |
| Display updates | Correct content shown | ⬜ |
