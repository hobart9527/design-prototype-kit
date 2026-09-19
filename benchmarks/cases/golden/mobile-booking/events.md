<!-- HIDDEN: never copied into a run workspace. Injected only when the trigger fires. -->
# Counterfactual Events: Mobile Booking

## Event 1 — Slot taken at payment
- trigger: 时段|定金|支付|确认|预约
- inject: 真实场景里常常是填完信息才发现时段被抢走了，这一步能不能不要退回重选。

## Event 2 — Older users struggle
- trigger: 触控|按钮|字号|可访问性
- inject: 我们的用户里有一半在 45 岁以上，手指不太灵活，按钮太小会点不中。
