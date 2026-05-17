# Bulk SMS Notifications

## Overview
Send SMS notifications to candidates for exam dates, payment reminders, schedule changes, and general announcements.

## Target Use Cases
1. **Exam Reminders** — Notify candidates of upcoming theory/practical exam dates
2. **Payment Reminders** — Alert candidates with outstanding balances (borxhi > 0)
3. **Schedule Changes** — Inform about cancelled or rescheduled lessons
4. **General Announcements** — Bulk messages to all active candidates or filtered groups

## Requirements
- Kosovo phone numbers (+383 prefix)
- SMS provider integration (e.g., Twilio, InfoBip, or local Kosovo provider)
- Bulk send with rate limiting
- Message templates with placeholders (candidate name, exam date, amount owed, etc.)
- Send history log per candidate
- Filter recipients by: category, status, instructor, payment status
- Opt-out support

## Database Changes
- `sms_templates` table — reusable message templates
- `sms_logs` table — sent message history (candidate_id, template, status, sent_at, cost)
- `candidates.phone` already exists

## UI
- New sidebar item under MENAXHIMI or FINANCAT
- Template editor with placeholder insertion
- Recipient filter/preview before sending
- Send history with delivery status

## Albanian UI Labels
- Mesazhet SMS = SMS Messages
- Dërgo SMS = Send SMS
- Shablloni = Template
- Marrësit = Recipients
- Dërguar = Sent
- Dështuar = Failed
- Historiku = History

## Priority: Low (future feature)
