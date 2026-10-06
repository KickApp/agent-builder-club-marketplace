# Kick binding: download-kick-document

How to get a presigned URL on Kick. Kick publishes its own skill guides:
discover with `list_kick_skills`, load with `load_kick_skill`. The guides own the
tool call shapes; this file maps them to the Procedure and adds what no guide
carries. On a rejected call, trust the live error, fix, retry once, report the
discrepancy.

## Guides to load

| Procedure step | Published guide | For |
| --- | --- | --- |
| 1. Get a fresh URL | `kick/documents-attach` | `documents_download` and document lookup. Load it for the call shape. This skill never uploads or attaches. |

## What no guide carries

- `documents_download { documentId: 12345 }` returns a presigned URL. `documentId`
  is numeric. The URL expires in minutes.
- A name with no id: `documents_query { operation: "search", search: "<filename or description>" }`
  resolves the numeric id. Search matches filename and metadata, not the text
  inside the file. Confirm with `documents_query { operation: "get_metadata", documentId }`
  when more than one row comes back. If the loaded guide names the operation
  differently, follow the guide.
- The URL is for Procedure step 2 (save the file). Fetching the URL over HTTP, or
  reading the document inside Chrome, skips the save.

## How another skill points here

In that skill's `references/kick.md`, one line:

When a step needs the file behind a Kick document, invoke `download-kick-document`
with the document id. The presigned URL stays inside that skill.
