---
name: download-kick-document
description: "Saves a Kick document as a local file from a fresh presigned download URL, then reads that file. Use when a skill or a user needs the contents of a document stored in Kick, when a signed download URL has to be opened, or when another skill's Kick binding points here for the file. Read-only."
---

# Download Kick document

## Purpose

Get a Kick document onto disk as a file, then read the file. A signed download URL
is the handle for saving. The saved file is what the rest of the work reads. Other
skills point here from their Kick binding and pass the document id.

1. Get a fresh download URL
2. Save the file
3. Read the file

## Procedure

- [ ] 1. Start from a document id, or from a URL returned moments ago. On Kick, the
      call is in `references/kick.md`.
      A URL from earlier in the conversation is stale. Request a new one. Request one document's URL, save that file, then request the next.
- [ ] 2. Save the file.
      Claude in Chrome is connected: open the URL, save it as a file, and close the tab. Chrome's job ends at the save.
      Claude in Chrome is not connected: give the user the link and ask them to click it. If this session can read the downloads folder, take the file that just arrived. If it cannot, ask them to attach the file to the conversation.
- [ ] 3. Read the saved or attached file. Figures and text in the handoff come from
      that file.

## Guardrails

- **Chrome saves, then the tab closes.** Scrolling, zooming, or describing the page
  on screen means the document was read in the browser. Close the tab as soon as
  the save finishes, and read the file.
- **A failed save gets a new URL.** The tell: a link that errors, or a request to
  re-read a document later in the conversation. Discard the old link and request a
  fresh one. Hand forward the file.
- **Several files in downloads, or several document matches: ask.** Show the names.
  The user picks.
- **Read-only.** This skill retrieves a file. It does not upload, attach, rename, or
  change a Kick record.
- On a rejected call, trust the live error over this skill's text, fix, and retry once.
  Never edit this skill file mid-run. If the working call differs from this skill, the
  handoff includes a method note naming what changed.

## Example

June operating bank statement, document id in hand. Chrome is connected.

Fresh URL, save `june-operating-statement.pdf`, close the tab, read the PDF.
Handoff: "June operating statement, statement date June 30, ending balance $42,180.
File: june-operating-statement.pdf."

Chrome is not connected.

"Download link, good for a few minutes: <url>. Click it. I will take the file from
your downloads if I can see that folder. If I cannot, attach it here."

Then the same handoff, read from the file.

## Completion

Done when:

- [ ] Each requested document is a file on disk or an attachment, and it was read
      from that file
- [ ] Any browser tab opened for the save is closed
- [ ] No Kick record was uploaded, attached, or changed

Cleanup: hand the file path, or the attachment, to the skill that asked. Discard
the URL. An ambiguous match stays an open question for the user.
