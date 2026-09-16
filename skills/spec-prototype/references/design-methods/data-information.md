# Craft reference — Data and complex information

Owns representation choice, complete work patterns and responsive data grids. **Open lens:** which
representation lets this user scan, compare and act on the actual attributes fastest? **Floor:**
responsive collapse, filtering, sorting and batch/action state remain coordinated.

Read this pillar when the decision is about the information itself, not only its styling.

Sections in this pillar:
- [Design information for decisions and repeated work](#design-information-for-decisions-and-repeated-work) - representations, work patterns and responsive data grids

## Design information for decisions and repeated work

Read for data interpretation, search/filtering, multi-item comparison, batch work
or a long transaction. Use sourced objects/operations; IA owns organization and
interaction-craft owns transition behavior. This method chooses representations
and task patterns before component styling or library selection.

| Double Diamond phase | Work and hand-back |
|---|---|
| Discover | Inventory real records, fields, units, ranges, missing values and task frequency. Walk what must be found, compared or changed together; retain source constraints and the uncertain decision. |
| Define | State the question users must answer and information they need simultaneously. Fix data meaning, action scope and a representative difficult case before selecting containers. |
| Develop | Compare credible representations or work patterns using the same records and task. Include an outlier, a missing value and long content when the data permits; measure precision, recall work and navigation cost. |
| Deliver | Answer the intended question from the rendered display, then perform the authorized action and return. Verify values, scope and retained context. Hand selected representation, field/encoding rules and task evidence to Foundation/Contract/Specification. |

### Choose representations from the question

| Judgment | Candidate | Inspect before selection |
|---|---|---|
| Retrieve exact values or compare several attributes | Aligned table or comparison list | Labels/units remain associated with values; required attributes survive narrow layout |
| Compare magnitude or rank | Common-baseline position/length, ordered table | Bar magnitude uses a truthful baseline; ordering does not imply unsupported priority |
| Follow change over time | Line/point series with explicit temporal spacing | Gaps are missing observations, not zero; irregular intervals and aggregation remain visible |
| Understand distribution | Binned or individual-value view with counts/context | Bin choices and small samples do not imply unjustified patterns |
| Understand relations | Linked rows, matrix or diagram | Edge meaning and direction are explicit; proximity alone does not assert causality |

Treat units, denominator, period, aggregation and missingness as data semantics.
For each displayed metric, map counted quantity → unit → period/aggregation →
missing-value rule → visible label/header/axis context in every representation.
A unit in the brief or a detail page cannot explain an unqualified number in the
current overview. Put the unit once in a clearly associated shared header/legend,
or beside the value when the compact layout removes that context; repeating it
in every cell is unnecessary when the shared meaning stays clear. Distinguish a
period total from a per-period average through the visible label and definition.
At handoff, include the overview-to-detail and wide-to-narrow representations in
this field-meaning map. Verify that the intended numerical question can be answered
from each actual view without consulting the source brief or memorizing another
page's units. Keep this alongside the selected representation in Specification,
not a second data model.

Keep zero, unknown and not applicable distinct. Explain a truncated scale when it
is defensible; never distort marks for visual balance. Use labels and an accessible
value alternative where visual encoding is essential. Reconcile displayed totals
with the source fixture and current filter. A chart is unnecessary when a clear
table answers the actual question better.

### Compose complete work patterns

For search/filter/sort, specify the scope searched, matching behavior, active
constraints, result count, empty/no-match distinction and return context. Preserve
unrelated selection/drafts according to the retained Contract. Choose immediate
versus explicit filter application based on cost and predictability, not fashion.

For authorized batch actions, expose which records are selected, whether selection
crosses pages/filters, and which are eligible. Before commitment make action and
scope understandable. For partial failure, identify affected records and permit
only sourced recovery; success must not imply every selected record changed.
Compare batch efficiency with individual control on a heterogeneous selection.

For a long transaction, compare a direct form, guided stages or a resumable task
list using dependencies and the user's need to revisit evidence. Show prerequisites
before they cause backtracking; preserve supported drafts and reviewable answers.
Introduce a task list only when transaction length/return needs justify it.
[GOV.UK's task pattern](https://design-system.service.gov.uk/patterns/complete-multiple-tasks/)
is a bounded reference for resumable transactions, not a universal wizard recipe.

Novice explanations and repeat-use efficiency may coexist: keep essential clues
visible, progressively disclose optional instruction, and add shortcuts only if
within scope. Verify the first attempt and a second different item. Hand resulting
state/continuation cases to [interaction craft](interaction-power.md#develop-an-interaction-model-around-the-users-judgment); do not create
a separate operation state model here.

### Responsive data grids and complex tables

When data contains many columns or high density, plan the physical multi-device
behavior before writing markup. Never allow unmanaged horizontal window overflow.

- **Narrow viewport table collapse (320px–390px):** Choose between:
  - *Table-to-Card transform:* Each row transforms into a structured card, pairing
    field labels with values. Best for records with distinct identities.
  - *Pinned key column + horizontal scroll:* Pin the primary identifying column
    (e.g., Name/ID) and trailing action column; scroll intermediate metrics
    horizontally with visible overflow gradient indicators.
  - *Priority column suppression:* Show only high-priority columns on mobile; provide
    a chevron to expand secondary fields in place or in a sheet.
- **Facet filter coordination:** When multiple filter dimensions exist (status, date,
  category, search query), display active filters as dismissible chips with count
  badges. Provide a single "Clear all" action. If filtering yields zero results,
  render a dedicated Empty Filter State explaining which filter caused the zero count
  and providing a one-tap reset.
- **Virtualization and layout stability:** For lists exceeding 50 items, preserve
  consistent row heights to prevent scroll jitter. Use layout-stable skeleton rows
  during data fetching instead of content-shifting loading spinners.
