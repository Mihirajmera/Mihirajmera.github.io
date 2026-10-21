---
title: What policy-as-code found in my own Terraform
description: I put three of my own AWS Terraform projects through a compliance gate. Two security Lambdas had permissions that would have broken the fix they exist to apply.
date: 2026-10-21
question: What happens when you hold your own infrastructure code to the evidence standard you'd ask of anyone else?
method: Scanned three Terraform projects with Checkov, mapped every result to NIST 800-53 and CIS AWS v3.0.0, fixed what was wrong, recorded a reviewed exception (with a reason and expiry) for everything else, and made CI fail on any finding without one.
tools: [Checkov 3.3, Terraform, GitHub Actions]
frameworks: [NIST 800-53, CIS AWS Foundations v3.0.0, OSCAL]
evidence:
  - {label: iam-zero-trust-security report, url: "https://github.com/Mihirajmera/iam-zero-trust-security/blob/master/compliance/report.md"}
  - {label: secure-vpc-architecture report, url: "https://github.com/Mihirajmera/secure-vpc-architecture/blob/master/compliance/report.md"}
  - {label: guardduty-siem-automation report, url: "https://github.com/Mihirajmera/guardduty-siem-automation/blob/master/compliance/report.md"}
numbers:
  - {n: "91", label: failed checks across three repos before any fixes, tone: red}
  - {n: "2", label: security Lambdas that couldn't do their job, tone: red}
  - {n: "0", label: findings left without a reviewed decision, tone: green}
---

## Why this matters

These three projects were already in CI with a misconfiguration scanner. The scan ran, printed a table and passed, because it was set not to fail. That's the most common state of "compliance as code": the check exists, and nothing depends on it.

So I changed the rule. Every finding must be **fixed**, or recorded as *risk-accepted*, *not-applicable* or *deferred*, with a reason and an expiry date. CI fails on anything else, including an exception that has expired.

## The two findings that mattered

Checkov flagged both remediation Lambdas for over-broad IAM permissions. Reading the code behind each finding showed something worse than over-permissioning:

- The **S3 remediation function** calls `s3:DeleteBucketPolicy` to remove a public bucket policy. Its role granted `ec2:TerminateInstances`, `ec2:StopInstances`, bucket ACL and policy writes on every resource, but **not** `s3:DeleteBucketPolicy`. The fix it exists to apply would have failed with AccessDenied.
- The **GuardDuty quarantine function** creates an isolation security group with `ec2:CreateSecurityGroup`. Its role granted terminate and revoke permissions it never used, but **not** `CreateSecurityGroup`. Isolating a compromised instance would have failed.

Both now grant exactly the calls their code makes, scoped to the resource types they touch. A scanner flagged the policies as too broad; only reading them against the code showed they were also too narrow where it mattered.

## The other fixes

Egress in the "zero trust" network allowed all traffic to anywhere; it's now the ALB to the VPC on port 80, the app to ports 80 and 443, and no egress from the database. CloudTrail log file validation was off (CIS 3.2). The default security group allowed traffic (CIS 5.4). Lambdas ran a deprecated Python runtime. Flow and findings logs were kept for 14 and 30 days; now a year.

## What the exceptions say

Of the rest, some are real and accepted (a break-glass admin role, now requiring MFA as well as the corporate network), some don't apply to a reference deployment (cross-region replication, X-Ray), two are scanner false positives (documented with the reason), and the HTTPS work is *deferred* with a date. Each one is a decision someone can review, not a suppression.

## What I'd tell a team adopting this

- **A scan that can't fail is a report, not a control.**
- **Read the finding against the code.** "Too broad" was the scanner's verdict; "missing the one permission it needs" was the real risk.
- **Exceptions need expiry dates.** Otherwise "accepted for now" becomes permanent.
