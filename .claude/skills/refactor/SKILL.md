---
name: refactor
description: "Surgical code refactoring — gradual improvements to structure and maintainability without altering external behavior. Identifies code smells and applies safe refactoring patterns."
---

# Refactor Skill

Surgical code refactoring — gradual improvements to structure and maintainability without altering external behavior.

## Golden Rules

1. **Behavior is preserved** — no functional changes
2. **Small steps** — incremental improvements
3. **Version control is your friend** — commit often
4. **Tests are essential** — verify at each step
5. **One thing at a time** — single responsibility per refactor

## When NOT to Refactor

- Under tight deadlines
- On critical production code lacking tests
- Without clear purpose

## Code Smells and Solutions

1. **Long methods** — Extract focused functions from bloated routines
2. **Duplication** — Consolidate repeated logic into shared utilities
3. **Large classes** — Divide responsibilities across specialized classes
4. **Parameter overload** — Group related parameters into objects
5. **Feature envy** — Move methods to objects that own their data
6. **Primitive obsession** — Replace basic types with domain-specific classes
7. **Magic values** — Replace unexplained numbers with named constants
8. **Nested conditionals** — Use guard clauses and early returns
9. **Dead code** — Remove unused functions and imports
10. **Inappropriate intimacy** — Reduce deep object access through encapsulation

## Process Framework

1. **Prepare** — Ensure tests exist, commit current state
2. **Identify** — Understand the smell
3. **Refactor** — Small increments
4. **Verify** — Test thoroughly
5. **Clean up** — Update documentation

## Common Refactoring Operations

- Extract method/function
- Introduce parameter object
- Replace conditionals with polymorphism
- Move method to appropriate class
- Extract interface/protocol
- Inline unnecessary abstractions
- Rename for clarity
