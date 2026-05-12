# Screenshot capture checklist

Run the tool yourself (see [DEMO_GUIDE.md](../../DEMO_GUIDE.md)) and capture these screenshots so the documentation has real-app evidence instead of placeholders.

Save them in **this folder** (`docs/screenshots/`) with the exact filenames below. They are referenced from `DEMO_GUIDE.md`, `README.md`, and `docs/AMS_INSTRUCTOR_GUIDE.md`.

## Required (referenced from public docs)

| Filename | Capture from | Show this |
|---|---|---|
| `01_launcher.png` | Console window | Both green `[OK]` startup lines |
| `02_welcome.png` | http://localhost:8000 | Welcome screen with language picker + 5 paths visible |
| `03_interview.png` | Interview screen mid-flow | A question + live preview panel on the right |
| `04_polish_before_after.png` | Live preview close-up | Raw answer ⟶ polished version |
| `05_completion.png` | After last question | Quality summary + three download buttons |
| `06_pdf.png` | Open the downloaded PDF | First page of the generated CV |
| `07_ats.png` | After pasting a job ad | Matched + missing keyword chips |
| `08_trainer_list.png` | http://localhost:8001 | Participant table with status badges |
| `09_trainer_detail.png` | Click a row | Side-by-side raw vs polished + inline edit active |
| `10_trainer_bulk.png` | Multi-select rows | Bulk approve button highlighted |
| `11_dist.png` | File Explorer on `dist/` | The three `.exe` files |

## Optional (nice to have for pitch deck)

| Filename | Capture from | Show this |
|---|---|---|
| `12_consent.png` | Welcome screen | Consent checkbox close-up — "Saved only on this computer" |
| `13_rtl_arabic.png` | Welcome screen with Arabic selected | Full RTL layout |
| `14_cover_letter.png` | Cover letter section | Generated personalised letter |
| `15_my_data.png` | After clicking 🔒 Meine Daten herunterladen | The downloaded JSON in a text viewer |
| `16_audit_log.png` | SQLite browser on `ams_trainer.db` | `export_logs` table content |
| `17_keyboard_focus.png` | Press Tab through the app | A focus ring visible on the active element |

## Capture conventions

- **1280 × 800** browser viewport (consistent with how AMS desktops are usually configured)
- **Light theme** (don't enable a dark theme extension)
- **English captions hidden** in the screenshot — use the German UI (it's the default and the AMS audience)
- **No personal data** — use the fixture user "Maria Beispiel" with placeholder content
- **PNG, lossless** — no JPEG artefacts on text
- **Crop to the active region** (don't include the whole desktop)

Once captured, they are picked up automatically by the references in `README.md` and `DEMO_GUIDE.md` — no document edits needed.
