# Cocos 场景接线说明

当前目录已经提交两个真实 Cocos Creator 3.8.x 场景资产：

- `Boot.scene`：启动场景，挂载 `Boot.ts`，运行后自动加载 `Field`。
- `Field.scene`：露茵村第一张地图纵切片场景，挂载 `FieldController.ts`。

`FieldController` 仍保留运行时自举能力：如果没有手动绑定 `MapRenderer` / `OverlayUI`，它会自动创建 `AutoMapRoot`、`MapGraphics`、`Player`、`NpcRoot`、`PoiRoot` 和三条 Label。这样场景可以先跑通，再逐步替换成正式 UI 和美术节点。

## 推荐打开方式

1. 用 Cocos Dashboard 打开 `cocos-client/`。
2. 在 Assets 面板打开 `assets/scenes/Boot.scene`。
3. 点击预览。Boot 会加载 `Field.scene`。

也可以直接打开 `Field.scene` 预览当前地图纵切片。

## Field 场景结构

```text
Canvas
  Camera
  FieldRoot
    FieldController
```

运行后会自动生成：

```text
FieldRoot
  AutoMapRoot
    MapGraphics
    Player
    NpcRoot
    PoiRoot
  AutoOverlayUI
    StatusLabel
    ObjectiveLabel
    DetailLabel
    RefreshButton
    StoryButton
    ReadButton
    TrainButton
    LunchButton
    DinnerButton
    NpcProfileButton
    GreetButton
    RestButton
    ResetButton
```

## 后续手动接线目标

后面做正式 UI 和美术时，可以把自动节点替换成手动节点。运行时按钮已经能直接调用 Day 1 方法，手动接线只是为了正式布局和视觉：

- `FieldController.renderer` -> `MapRenderer`
- `FieldController.overlay` -> `OverlayUI`
- `MapRenderer.mapGraphics` -> `MapGraphics` 节点的 `Graphics`
- `MapRenderer.playerNode` -> `Player`
- `MapRenderer.npcRoot` -> `NpcRoot`
- `MapRenderer.poiRoot` -> `PoiRoot`
- `OverlayUI.statusLabel` -> `StatusLabel`
- `OverlayUI.objectiveLabel` -> `ObjectiveLabel`
- `OverlayUI.detailLabel` -> `DetailLabel`

## 可绑定到按钮的方法

把按钮 click event 目标指向挂有 `FieldController` 的节点：

- `refreshAll`
- `chooseFirstStoryChoice`
- `runReadingDemo`
- `runTrainingDemo`
- `runLunchDemo`
- `runDinnerDemo`
- `restUntilNextDay`
- `showNearestNpcProfile`
- `greetNearestNpc`
- `resetPrototype`

这些方法都走同一 FastAPI 后端，不在 Cocos 内部改写世界事实。机器可读清单见 `field.scene-manifest.json`。
