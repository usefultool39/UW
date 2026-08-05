# 素材权利、来源与 AI 生成记录规范

> 本文件是项目内部治理规范，不替代专业法律意见。目标是让每个进入游戏的文件都能回答“谁做的、从哪来、允许怎么用、经过什么修改”。

## 1. 可接受来源

- 项目成员原创并明确授权项目使用。
- CC0 / 公共领域素材。
- CC-BY 等允许商业游戏分发的素材，且项目能履行署名要求。
- 购买的素材包，许可明确覆盖游戏嵌入与发布。
- AI 工具生成输出，使用条款允许当前账号/套餐的商业使用，并保存生成记录。
- 仅做参考的摄影/建筑/服装图，但必须标记 `reference_only`，不得直接复制像素或独特设计。

## 2. 禁止进入 approved 的来源

- 官方动画/影视截图、游戏拆包、Wiki 截图、他人 fan art 未授权转载。
- 来源不明的 Pinterest/论坛/网盘二次上传。
- “免费下载”但没有许可文本的字体、音乐、音效、图标。
- 带品牌 logo、现实人物肖像、受保护角色定妆且无授权的内容。
- AI 输出明显复刻某一现有角色、作品 UI、艺术家签名风格或训练参考图构图。
- 许可禁止再分发、禁止修改、禁止商用，但项目需要这些权利的素材。

## 3. 特别原创化要求

项目的玩法方向可以借鉴“即时反馈、数值决策、叙事悬念、日程关系”，但素材不得复刻参考作品的：

- 角色面部与服装定妆。
- 标志性武器、徽章、卡牌边框、字体 logo。
- 完整 UI 布局或地图构图。
- 官方配乐旋律、音效采样、语音。

提示词使用可观察属性，不写“做成某作品/某艺术家的风格”。

## 4. AI 生成必须记录

- provider/tool：平台与工具。
- model/version：模型名称与版本（能获取时）。
- account/license：生成时账号套餐与商用条款链接/截图。
- prompt/negative prompt：完整文本。
- seed/settings：seed、分辨率、采样设置、参考图权重。
- reference images：每张来源和是否有权使用。
- edits：Photoshop、去字、局部重绘、混音等。
- creator/date：操作人和日期。

若平台不能提供明确商用权限，状态保持 `license_unknown`，只做内部方向讨论。

## 5. Sidecar 权利字段建议

```yaml
rights:
  owner: "姓名或组织"
  license: "owned | CC0 | CC-BY-4.0 | purchased-pack | provider-commercial-output | reference_only | unknown"
  source_url: "..."
  attribution_required: true
  attribution_text: "..."
  redistribution_allowed: true
  modification_allowed: true
  commercial_use_allowed: true
  evidence_path: "materials/inbox/licenses/..."
```

## 6. 字体特别规则

- 必须确认桌面分发、Web 嵌入、子集化、修改、再分发许可。
- OFL 字体通常可用，但仍保存许可证和字体名称要求。
- 不把系统自带商业字体文件复制进项目。
- 字体体积进入首屏预算；中文全集可能很大，接入前评估子集化与 fallback。

## 7. 音频特别规则

- “royalty-free”不等于“无条件再分发”；保存具体许可。
- 不接受从视频平台提取的音乐/环境声。
- 采样包要确认可用于游戏成品；不要单独再发布原始采样。
- 生成音乐保留无损 master 和平台条款证据。

## 8. 署名与发布

- 所有需要署名的条目汇总到项目 attribution 文件；当前 Kenney UI 许可继续保留。
- 正式发布前，从 manifest 自动/人工核对每个 integrated 素材的许可证。
- 如果权利状态后来变化，先恢复旧素材或程序化 fallback，不删除证据。
