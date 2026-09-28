# Privacy & Limitations

## Privacy Approach

Recommended behavior for the prototype:

- process frames locally,
- do not store raw camera images unless explicitly required for testing,
- do not perform identity recognition,
- do not build persistent user profiles,
- keep only non-identifying runtime statistics if analytics are needed.

## Classification Limitations

Visual appearance is not a reliable way to determine a person's actual gender identity.

The system should therefore be presented as a classifier operating on the labels present in its training data, not as a definitive gender detector.

Possible errors can result from:

- lighting,
- pose,
- occlusion,
- camera quality,
- dataset bias,
- demographic imbalance,
- ambiguous or out-of-distribution inputs.

## Safe Product Behavior

Use a confidence threshold and a neutral fallback content option when confidence is low.

The output should not be used for consequential decisions.
