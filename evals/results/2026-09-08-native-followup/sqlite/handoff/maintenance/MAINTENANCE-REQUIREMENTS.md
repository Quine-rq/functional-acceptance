# Frozen synthetic maintenance scenario

This requirement was proposed and approved by the evaluation coordinator on 2026-09-08 before the maintenance run. It extends the existing generic contact data-fidelity goal for evaluation; it does not represent external user feedback or a new sqlite-utils product rule.

Start only after an independent executor has replayed the candidate-generated native regression pack without the Skill. Preserve that replay's original evidence. The maintenance run gets a separate fresh copy and new run evidence.

Extend the contact synthetic input with the explicit scalar fields `postal_code` and `preferred_name` in every contact record. Include a postal code such as the JSON string `"00123"` so that leading zeroes and string identity can be observed, and include both `preferred_name: null` and `preferred_name: ""` among the records. Do not infer expected conversion from current automatic type inference: the requested input values and their JSON scalar types must survive exactly.

Retain the prior contact fields and checks: Unicode, multiline strings, quoted strings, complete contact import and fresh-process CLI readback, retained CLI JSON export compared by stable contact id, ordinary duplicate-id refusal with every previously stored contact unchanged, and unrelated pre-existing table/row preservation. JSON object key order, whitespace, and incidental result order are not requirements. Do not introduce omitted-field defaults, boolean conversion, or conflict-resolution semantics.

Maintain the generated native pytest pack using its documented setup and repeat entrypoint. Change only run-owned acceptance fixtures, relevant assertions, and handoff documentation needed for these explicit fields. Do not edit upstream source/tests/configuration, the original onboarding requirements, previous evidence, or any Skill. Keep every failed attempt, do not delete or weaken assertions to obtain green results, and attribute product counterexamples separately from test faults and missing evidence.

Record preparation, changes, diagnosis/corrections, actual command results, new evidence locations, and cleanup/retention. This one synthetic maintenance exercise cannot establish external-human usability or long-term savings.
