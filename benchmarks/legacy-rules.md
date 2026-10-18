# Legacy benchmark-specific rules

These constraints apply only when running the named legacy benchmark scenarios. They are not global product requirements. Source rule IDs below identify the owning general rule in `skills/spec-prototype/references/03-verification/lean-delivery-rules.md` or the source stage text.

## CRAFT-STATE-ENTRY

- Accept the benchmark's common aliases: `?state=conflict` and `?state=taken` for a slot-taken conflict; `?state=empty` and `?state=empty-queue` for an empty list; `?state=service_selected` lands on slot selection with service, technician and customer info preselected. Record the alias set in the design record.
- For a mid-flow benchmark state (`service_selected`, `slot_chosen`, `timeslot_conflict`), seed upstream decisions (service, tech, slot) and land on the step where the state is observable, not step 1.

## CRAFT-TASK-COPY

- In the mobile-booking benchmark, when the brief names a deposit (`付定金`), show its amount and a currency unit (`¥`, `￥`, `元`) beside the commit control; the commit control uses a task verb from the brief (`确认`, `预约`, `支付`, `下单`, `提交`) rather than only a navigation verb.
- Preserve the brief's exact conflict wording, e.g. `已占用` when the brief says `时段已被占用`; prefer the shortest canonical form (`时段已占用`, not `这一格已被占用`).

## CRAFT-ACTION-FEEDBACK

- For an auditable decision with supplied actor/timestamp vocabulary, examples include `已通过 · 审批人` and `已打回 · 10/15 20:51`; a disappearing `已通过` toast alone is not a terminal record.
- For a benchmark that explicitly asks for an auditable record surface, example rendered text may include `已审批|审批记录|审批人|通过时间|history|记录`.

## CRAFT-AUDIT-RECORD-SEEDING

- In the legacy operational-console benchmark with `待办` and `审批记录` / `审计日志` tabs, seed pending items and 1–2 already-processed items. Processed items retain terminal status in both the record tab and queue rows.

## CRAFT-REVISION-COMPARE

- The legacy document-revision benchmark uses paragraph anchors such as `¶2` or `第 3 段`; its rendered text includes revision/change vocabulary such as `修订|版本|变更|revision|diff|对比`.

## Stage 1 benchmark examples

- Examples retained from the source stage: a `5-minute undo window`, `零长列表`, the three-phase labels `止血/收敛/收尾`, an expert-operator/drill-cadence rationale, `误下线/未经预览`, invented `剩余容量` / `CPU水位` metrics, and the operational object `批次`. They are scenario examples only, not global requirements.
