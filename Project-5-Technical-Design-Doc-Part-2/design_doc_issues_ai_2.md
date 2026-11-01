# Bend Bike Shop Technical Design Document — AI Issues Report 2

## Review Scope

This is a partial technical design document. Sections 8–11 intentionally provide a sampling of data models, interfaces, invariants, and failure modes rather than a complete implementation specification. The following findings focus on logical and structural inconsistencies within the documented design; missing exhaustive coverage is not treated as a defect.

## Issue 1: Pending Reservation Holds Are Not Represented in the Data Model

**Issue:** Sections 9.3 and 10.1 require temporary holds to expire and distinguish unexpired pending reservations from expired ones, but the Reservation entity has no hold expiration field.

**Why This Matters:** Availability checks cannot reliably determine when an abandoned pending allocation stops blocking a bicycle.

**Recommendation:** Add a nullable `hold_expires_at: datetime` field to Reservation, or document an equivalent mechanism for tracking hold expiration. Clarify that expired holds do not count as active allocations.

## Issue 2: Payment and Waiver Evidence Is Missing From the Four-Entity Sample

**Issue:** Section 10.2 requires verified waivers and successful payments before confirmation, but Section 8 does not show where verification status or processor references are stored.

**Why This Matters:** The system must be able to enforce and audit the confirmation rule after external-service calls.

**Recommendation:** Explain that the four-entity ER diagram is illustrative, and that payment and waiver references are additional fields or records outside the sampled entities. Do not expand the required four-entity diagram unless desired.

## Issue 3: Cancellation Can Leave an Empty Active Reservation

**Issue:** Section 9.6 cancels an individual reservation item while guaranteeing other active items are unchanged, but does not say what happens when the canceled item is the last active item. Section 8 shows a reservation containing one or more items.

**Why This Matters:** The reservation could remain `CONFIRMED` even though it has no active bicycles.

**Recommendation:** Specify that canceling the last active item transitions the reservation to `CANCELED`, while retaining canceled items for history. Clarify that the one-or-more relationship includes historical canceled items.

## Issue 4: Interface Error Contracts Are Inconsistent

**Issue:** `createReservation()` returns `Reservation` but does not define an error outcome. `verifyWaiver()` returns `False` both when the waiver is incomplete and when the provider cannot be reached. Boolean cancellation and maintenance results similarly hide the reason for failure.

**Why This Matters:** Callers need to distinguish validation errors, access denial, conflicts, and temporary external-service outages.

**Recommendation:** Add a concise shared error-handling convention (such as documented error codes or exceptions), without needing to redesign all six signatures.

## Issue 5: Maintenance Authorization Should Not Rely on a Supplied Manager ID Alone

**Issue:** `markBicycleForMaintenance(bicycle_id, manager_id)` accepts a manager ID and requires manager permissions, but does not explicitly state that the ID must match the authenticated staff identity.

**Why This Matters:** A client-supplied ID alone is not proof of authorization.

**Recommendation:** State that the backend derives or validates manager identity from the authenticated session and records the actor in an audit trail.

## Issue 6: Payment Retry and Confirmation Need an Explicit Atomicity Strategy

**Issue:** Section 9.5 says to check processor status after a timeout, while Section 11 says not to confirm until payment success is verified. The design does not explain how it avoids duplicate charges or reconciles a successful charge if the database update fails.

**Why This Matters:** A payment could succeed externally while the reservation remains pending locally.

**Recommendation:** Describe use of a stable payment attempt reference or idempotency key, processor status reconciliation, and a safe pending/review state before retrying or confirming.

## Issue 7: Reservation Item Status Values Are Not Defined

**Issue:** Section 8 includes a `status` field for ReservationItem, and Section 9.6 uses `CANCELED`, but Section 9.1 defines only ReservationStatus and BicycleStatus.

**Why This Matters:** Implementers may confuse item-level and reservation-level state transitions.

**Recommendation:** Define a small `ReservationItemStatus` enum, such as `ACTIVE`, `CANCELED`, and `RETURNED`, and clarify how it relates to the parent reservation status.

## Issue 8: Failure Mode Table Format Needs Verification

**Issue:** Section 11 uses columns for Failure Mode, Cause, Effect, and System Response. The assignment asks for the format shown in the Failure Modes exploration, which was not included in the reviewed file.

**Why This Matters:** The content covers four failure scenarios, but the headings may not match the instructor's example.

**Recommendation:** Compare the table against the exploration and adjust column headings or content only if necessary.
