# Contact import, retrieval, and preservation acceptance

A person moving a small contact list into a local SQLite database must be able to retrieve every contact in a later CLI process and export the stored list back to JSON without losing or changing values.

Use a small synthetic contact JSON array whose stable primary key is `id`. Include Unicode, a multiline string, a string with quotes, and an explicit null among its fields. The contact records and scalar field values, including null and empty-string distinctions where present, must round-trip exactly. Compare by contact id; incidental JSON whitespace and object-key order are not user requirements.

The journey starts with an isolated database containing an unrelated table and row. Import the contacts through the project's normal CLI, then observe their persisted values through a newly launched CLI process. Export through the CLI to a retained JSON artifact and verify its complete contents against the input.

An ordinary insert using a contact id that is already stored must be refused visibly. That refusal must leave all previously stored contacts unchanged, including the existing record at that id. The unrelated table and its row must remain unchanged throughout the journey.

Leave a project-native pytest regression pack plus enough setup, repeat-run, evidence, and cleanup instructions for a different executor who does not have this Skill or conversation. Keep original failed attempts if anything fails. Findings must distinguish executed observations, missing evidence, and retained local artifacts. This is an isolated local CLI acceptance exercise; it is not an authorization to change the application or claim production readiness.
