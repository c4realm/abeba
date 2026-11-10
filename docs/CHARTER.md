# Equb Charter (business rules, v1)
- Terms are versioned, hashed, frozen at start; every member accepts (timestamp + hash). 18+ and verified email.
- Slots: Early (first ~30%), Middle, Late (last ~30%). Lottery order drawn once, seed logged.
- Holdback on payout = tier rate x remaining obligations (Early 30%, Middle 10%, Late 0%). Guarantor replaces holdback.
- Early premium 2% of pot, shared by Late members with no uncured default. Set-off against own future payout.
- Ladder: reminders D-48h/-24h > Due D 23:59 > Late (grace, default 2d, no fee) > Overdue: one-time fee C x p (default 5%, cap 10%) + Default Notice with 3-day cure > Dispute pauses clock > Defaulted: cover from holdback, guarantor, payout claim; standing Restricted (can still pay).
- Payments: sandbox success auto-confirms; cash needs member acknowledgement (48h); payout receipt auto-confirms 72h.
- Ledger is immutable; balances computed. Audit log is append-only and hash-chained. Admins cannot edit money, only suspend/dissolve/resolve with reason.
- Lifecycle: Draft > Recruiting > Locked > Active > Completed/Dissolved. New organizers: max 10 members, 3 groups.
