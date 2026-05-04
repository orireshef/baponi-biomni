---
name: create-prd
description: Create comprehensive Product Requirements Document for an epic through collaboration between Technical PM and AI Researcher agents. Use when ready to define detailed requirements for an epic.
---

# Create PRD for Epic

**Usage**: `/create-prd <epic_number>`

## Process Overview

This skill orchestrates PRD creation through multi-agent collaboration:

1. **Technical PM agent** - API design, user stories, requirements structure
2. **AI Researcher agent** - Research methodology, metrics validation, feasibility
3. **User** - Requirements clarification and final approval

## Directory Structure Context

```
docs/
├── SCDIC Final Algorithm Spec v14.0.md   # Mathematical foundation
├── architecture.md                       # System design & testing
└── epics/
    ├── README.md                          # Overview & dependencies
    └── epic_N/
        ├── overview.md                    # Epic specification (READ FIRST)
        ├── prd.md                         # Output of this command
        └── solution_design.md             # Created after PRD approval
```

## Execution Steps

### Phase 1: Spawn Technical PM Agent

Spawn `technical-pm` agent to:
- Read required documents (README, architecture, algorithm spec, epic overview)
- Draft initial user stories and functional requirements
- Propose API contracts for key interfaces
- Identify technical constraints and dependencies

### Phase 2: Spawn AI Researcher Agent

Spawn `ai-researcher` agent to review PM's analysis:
- Validate research methodology assumptions
- Challenge performance targets for feasibility
- Assess experimental design implications
- Identify missing metrics or validation strategies

### Phase 3: Joint Question Formation

Both agents collaborate to formulate 3-8 clarifying questions:
- **Requirements**: Ambiguities in scope or functionality
- **Priorities**: Trade-offs between features
- **Technical**: Architectural decisions with multiple valid approaches
- **Research**: Experimental design or metric choices
- **Scope**: In/out boundaries, edge cases

Use `AskUserQuestion` tool with:
- Clear context for each question
- 2-4 options with trade-offs explained
- Recommendations when appropriate

### Phase 4: PRD Drafting

After receiving user answers, create comprehensive PRD with:

**Required Sections**:
1. Executive Summary (problem, goals, constraints)
2. User Stories (5-10 stories with acceptance criteria)
3. Functional Requirements (FR-N.M with API contracts)
4. Non-Functional Requirements (performance, reliability, testability, security)
5. Success Metrics (primary must-haves, secondary nice-to-haves)
6. Out of Scope (explicitly deferred features)
7. Risks & Mitigations (likelihood, impact, fallback plans)
8. Dependencies (external, internal, downstream consumers)
9. Open Questions (unresolved decisions)
10. Acceptance Criteria Summary (checklist format)

**API Contract Format**:
```python
# Show concrete Python code with:
from scdic.module import Class

# Realistic example with actual data
result = Class.method(param="bird/financial", sql="SELECT ...")

# Document return type with comment
# Returns: ResultObject(
#   field1=value,
#   field2=value,
#   ...
# )

# Show error case
try:
    result = Class.method(invalid="...")
except SpecificError as e:
    # Returns actionable error message
```

### Phase 5: Review & Approval

Both agents review PRD for:
- ✅ Completeness (covers all overview.md deliverables)
- ✅ Consistency (user stories → FRs → success criteria align)
- ✅ Measurability (all NFRs and metrics are verifiable)
- ✅ Actionability (developers can implement from this)

Present to user for approval before saving to `docs/epics/epic_N/prd.md`.

## Quality Standards

### Must Have:
- All user stories map to functional requirements
- All functional requirements have concrete API contracts
- All NFRs are measurable and verifiable
- Success criteria cover all deliverables from overview
- Out-of-scope section prevents misunderstandings

### Must Not Have:
- Vague requirements ("should work well", "fast enough")
- Implementation details (that's for solution_design.md)
- Scope creep (features not in overview.md)
- Unmeasurable success criteria

## Anti-Patterns to Avoid

1. **Skipping Context Gathering**: Must read all related docs first
2. **No User Clarification**: Must ask questions on ambiguities
3. **Vague APIs**: Show concrete code examples, not pseudocode
4. **Specification by Implementation**: Describe outcomes, not algorithms
5. **Success Theater**: Metrics must be measurable and verifiable

## Output Location

PRD saved to: `docs/epics/epic_N/prd.md`

Commit immediately after approval for version control.

## Important Notes

- **Time Investment**: 30-60 minutes for thorough PRD creation
- **Iteration**: Expect 2-3 rounds of clarification with user
- **Research vs Product**: Distinguish experimental features from production requirements
- **API Stability**: Epic 0-2 APIs are UNSTABLE, stabilize after Epic 2

**Remember**: A great PRD saves weeks of rework during implementation. Invest the time upfront.
