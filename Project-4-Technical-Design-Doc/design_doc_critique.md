# Bend Bike Shop Technical Design Document — AI Critique

## Overview

After reviewing the AI-expanded Technical Design Document, I selected three additions to evaluate. I considered whether each suggestion would improve the Bend Bike Shop system, whether it made sense for the business, and whether any changes or additional decisions would be necessary.

## Critique 1: Temporary Reservation Holds

**AI Addition:** Section 9.1 — New Customer Reservation

The AI suggested using temporary reservation holds that automatically expire if a customer does not complete checkout.

**My Evaluation:**

I agree with this suggestion because it prevents customers from holding bicycles indefinitely without completing their reservations. For example, if someone selects a bicycle but closes their browser before paying, that bicycle should eventually become available to other customers.

I think this would help prevent problems with bicycle availability and make the reservation process more reliable. However, we would need to discuss the expiration time with Rodney before deciding how long a bicycle should remain on hold.

**Decision:** Accept the suggestion, but confirm the reservation hold duration with Rodney.

## Critique 2: Relational Database Design

**AI Addition:** Section 10 — Data Management and Storage

The AI proposed using a relational database with ten logical entities to manage information about customers, bicycles, reservations, payments, refunds, inspections, and maintenance.

**My Evaluation:**

I agree that a relational database makes sense for this system because we need to organize information and connect different records. For example, a customer might reserve multiple bicycles and later cancel only one of them. Having separate reservation and bicycle records would make it easier to manage those changes.

However, I am not convinced that all ten proposed entities are necessary. I think we should review each one and determine whether it serves an important purpose before committing to the database design. Adding unnecessary tables could make the system more complicated than it needs to be.

**Decision:** Accept the relational database approach, but review the ten proposed entities before finalizing the design.

## Critique 3: Guest Reservation Security

**AI Addition:** Section 11 — Security and Access Control

The AI recommended requiring additional verification before guest customers can access or modify existing reservations.

**My Evaluation:**

I agree with adding verification because customers should not be able to access or change someone else's reservation just by knowing their confirmation number. At the same time, I want customers to be able to make reservations without creating an account.

I think email verification codes would be a good solution. When a customer wants to modify or cancel a reservation, the system could send a one-time code to the email address associated with the booking. This would provide additional security without requiring customers to create usernames and passwords.

**Decision:** Accept the suggestion and recommend email verification codes for guest reservation access.

## Conclusion

Overall, I think the AI made useful additions to the Technical Design Document. The suggestions addressed problems that might not be obvious during the initial design process, including abandoned reservations, database organization, and customer security.

However, I do not think every AI recommendation should automatically become part of the final design. Some decisions, such as reservation hold durations and database structure, still need to be reviewed before implementation. AI can help identify possible solutions, but the final decisions should be based on the system's requirements and the needs of Bend Bike Shop.