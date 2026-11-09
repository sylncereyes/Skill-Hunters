# Test Finding

## Summary
Test IDOR finding

## Steps
1. GET /api/users/1
2. GET /api/users/2

## Impact
Access to other user data

## Remediation
Add authorization checks