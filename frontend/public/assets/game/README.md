# 游戏素材替换说明

这个目录是地图主界面当前使用的稳定素材目录。Vite 会把 `frontend/public` 直接作为网站根目录，因此这里的文件在前端里对应：

- `field-bg.png` -> `/assets/game/field-bg.png`
- `player-token.png` -> `/assets/game/player-token.png`
- `alice-token.png` -> `/assets/game/alice-token.png`
- `eugeo-token.png` -> `/assets/game/eugeo-token.png`

## 直接替换素材

想换素材时，最简单的做法是保持文件名不变，直接覆盖同名 PNG，然后刷新浏览器。

- 地图背景：替换 `field-bg.png`
- 玩家地图小人：替换 `player-token.png`
- 爱丽丝地图小人：替换 `alice-token.png`
- 优吉欧地图小人：替换 `eugeo-token.png`

角色 token 建议使用透明 PNG。背景图建议使用横版手绘地图，比例接近 16:9 或 3:2 都可以。

## 新增素材路径

如果不想覆盖同名文件，而是新增新文件，请同步修改：

`frontend/src/field/gameContentConfig.js`

这个文件集中管理地图主界面的章节标题、人物显示名、角色素材路径、场景名、时间段名称、任务提示和地标绘制配置。

`frontend/src/field/gameAssetPaths.js` 仍保留兼容旧引用，但新的内容扩展优先改 `gameContentConfig.js`。
