<!-- HIDDEN: never copied into a run workspace. -->
# Mock user: Content Studio

## Held Facts
- This workflow covers one article, with a current draft and retained prior revisions.
- Authors own the prose; editors may comment and request changes but may not silently rewrite the author's voice.
- A comment is anchored to a particular revision and passage.
- Resolved comments remain in history; a changed passage may warrant a new comment, not silently reopening the old one.
- Citation status can be verified, missing, or not yet checked. The product does not independently certify truth.
- No external publishing integration or AI rewrite exists in this release.
- Desktop is the primary editing surface; mobile is used by authors to inspect and reply.

## Decision Answers
- 自动改写|AI|改写: 不要自动替作者改稿，作者要保留自己的表达。
- 评论|意见|版本: 意见要能看出针对哪个版本和哪一段，旧意见的处理记录要保留。
- 引用|来源|核对: 可以标出已核对、缺失和还没核对，但不要说系统保证了内容真实。
- 发布|发布平台|集成: 这版只做发布前检查，不接外部发布平台。
- 手机|移动端: 作者在手机上至少要能查看意见并回复；完整编辑主要在桌面。
- 权限|编辑|作者: 编辑可以提意见和要求修改，最终文字由作者决定。

## Fallback
如果没有明确规定，不要增加协作角色、自动写作能力或外部集成。优先保留稿件、版本和意见之间清楚可追溯的关系。
