import { _decorator, Button, Component, EventMouse, Graphics, input, Input, Label, Node, tween, UITransform, Vec3 } from 'cc'
import { GameApi } from '../api/GameApi'
import {
  AgentState,
  DEFAULT_API_BASE,
  DEFAULT_WORLD_MAP_ID,
  MapData,
  PlayerActionBody,
  PlayerActionResult,
  SceneActivity,
  StoryChooseResult,
  StoryEvent,
  TimeBand,
  WorldState
} from '../api/contracts'
import { localBfsPath } from './LocalPath'
import { MapRenderer } from './MapRenderer'
import { OverlayUI } from '../ui/OverlayUI'

const { ccclass, property } = _decorator

@ccclass('FieldController')
export class FieldController extends Component {
  @property
  apiBase = DEFAULT_API_BASE

  @property(MapRenderer)
  renderer: MapRenderer | null = null

  @property(OverlayUI)
  overlay: OverlayUI | null = null

  private api: GameApi | null = null
  private map: MapData | null = null
  private state: WorldState | null = null
  private storyEvents: StoryEvent[] = []
  private sceneActivities: SceneActivity[] = []
  private busy = false
  private runtimeButtonNodes: Node[] = []

  async onLoad(): Promise<void> {
    this.ensureRuntimeWiring()
    this.api = new GameApi(this.apiBase)
    input.on(Input.EventType.MOUSE_UP, this.onMouseUp, this)
    await this.refreshAll()
  }

  onDestroy(): void {
    input.off(Input.EventType.MOUSE_UP, this.onMouseUp, this)
  }

  async refreshAll(): Promise<void> {
    if (!this.api) return
    this.overlay?.setStatus('Syncing backend world state...')
    const state = await this.api.getState()
    const map = await this.api.getWorldMap(state.player?.map_id || DEFAULT_WORLD_MAP_ID)
    const [story, activityCatalog] = await Promise.all([
      this.api.getAvailableStoryEvents(),
      this.api.getSceneActivities()
    ])
    this.state = story.state || state
    this.map = map
    this.storyEvents = story.events || []
    this.sceneActivities = activityCatalog.activities || []
    this.renderer?.render(map, this.state, this.storyEvents)
    this.overlay?.setContext(this.state, this.storyEvents, this.availableActivitiesForCurrentScene())
    this.overlay?.setStatus(`Day ${this.state.day} | ${this.state.time_band} | ${this.storyEvents.length} story events available`)
  }

  private async onMouseUp(event: EventMouse): Promise<void> {
    if (this.busy || !this.api || !this.map || !this.state || !this.renderer) return
    const loc = event.getUILocation()
    if (this.isRuntimeButtonHit(loc)) return
    const tile = this.renderer.uiToTile(loc)
    if (!tile) return
    await this.moveTo(tile.x, tile.y)
  }

  private async moveTo(tileX: number, tileY: number): Promise<void> {
    if (!this.api || !this.map || !this.state || !this.renderer) return
    const path = localBfsPath(this.map, { x: this.state.player.tile_x, y: this.state.player.tile_y }, { x: tileX, y: tileY })
    if (!path || path.length < 2) {
      this.overlay?.setStatus('That tile is not reachable yet.')
      return
    }

    this.busy = true
    this.overlay?.setStatus('Moving...')
    await this.playLocalPath(path)
    const result = await this.api.playerAction({
      kind: 'move_map',
      map_id: this.map.id,
      tile_x: tileX,
      tile_y: tileY
    })
    if (!result.ok) {
      this.applyActionResult(result)
      this.overlay?.setStatus(`Move failed: ${result.error || 'blocked'}`)
    } else {
      this.applyActionResult(result)
      this.overlay?.setStatus(`Arrived at ${this.state.player.scene_id}`)
    }
    this.busy = false
  }

  async chooseFirstStoryChoice(): Promise<void> {
    const event = this.storyEvents[0]
    const choice = event?.choices?.[0]
    if (!event || !choice) {
      this.overlay?.setStatus('No selectable story event is available right now.')
      return
    }
    await this.chooseStory(event.id, choice.id)
  }

  async runReadingDemo(): Promise<void> {
    await this.runSceneActivity('church_read_sacred_arts', 'trace_silence')
  }

  async runTrainingDemo(): Promise<void> {
    await this.runSceneActivity('gigas_chop_rhythm')
  }

  async runLunchDemo(): Promise<void> {
    await this.runSceneActivity('church_ask_alice_lunch', 'support_eugeo')
  }

  async runDinnerDemo(): Promise<void> {
    await this.advanceUntilTimeBand(['evening', 'night'])
    await this.runSceneActivity('home_evening_meal', 'side_alice')
  }

  async restUntilNextDay(): Promise<void> {
    await this.runPlayerAction({ kind: 'rest_until_next_day' }, 'Rest complete. A new day begins.')
  }

  async showNearestNpcProfile(): Promise<void> {
    if (!this.api || !this.state) return
    const npc = this.nearestNpc()
    if (!npc) {
      this.overlay?.setStatus('No NPC is nearby.')
      return
    }
    const out = await this.api.getNpcProfile(npc.id)
    const rel = out.profile?.relationship || {}
    this.overlay?.setStatus(`${npc.id} profile: trust=${rel.trust ?? 0}, affinity=${rel.affinity ?? 0}, tension=${rel.tension ?? 0}`)
  }

  async greetNearestNpc(): Promise<void> {
    if (!this.api || !this.state) return
    const npc = this.nearestNpc()
    if (!npc) {
      this.overlay?.setStatus('No NPC is nearby.')
      return
    }
    const out = await this.api.sendDialogue(npc.id, 'Anything in the village I should record today?', {
      scene_id: this.state.player.scene_id,
      client: 'cocos-v0'
    })
    this.overlay?.setStatus(out.ok ? `${npc.id}: ${out.reply || '...'}` : `Dialogue failed: ${out.error || 'unknown'}`)
  }

  async resetPrototype(): Promise<void> {
    if (!this.api) return
    const out = await this.api.reset()
    this.state = out.state
    await this.refreshAll()
  }

  private async chooseStory(eventId: string, choiceId: string): Promise<void> {
    if (!this.api || this.busy) return
    this.busy = true
    this.overlay?.setStatus('Submitting story choice...')
    try {
      const out = await this.api.chooseStoryEvent(eventId, choiceId)
      this.applyStoryResult(out)
      this.overlay?.setStatus(out.ok ? 'Story choice saved to relationship and memory state.' : `Story choice failed: ${out.error || 'unknown'}`)
      await this.refreshStoryEventsOnly()
    } finally {
      this.busy = false
    }
  }

  private async runSceneActivity(activityId: string, choiceId?: string): Promise<void> {
    const activity = this.sceneActivities.find((item) => item.id === activityId)
    if (!activity) {
      this.overlay?.setStatus(`Activity not found: ${activityId}`)
      return
    }
    await this.ensureActivityScene(activity)
    await this.runPlayerAction(
      {
        kind: 'interact_with_hub',
        poi_id: activity.poi_id,
        activity_id: activityId,
        activity_choice: choiceId
      },
      `${activity.label || activity.title} complete.`
    )
  }

  private async ensureActivityScene(activity: SceneActivity): Promise<void> {
    if (!this.state) return
    const allowed = activity.scene_ids?.length ? activity.scene_ids : activity.scene_id ? [activity.scene_id] : []
    if (!allowed.length || allowed.includes(this.state.player.scene_id)) return
    await this.runPlayerAction({ kind: 'enter_scene', scene_id: allowed[0] }, `Entered ${allowed[0]}`)
  }

  private async advanceUntilTimeBand(targets: TimeBand[], maxSteps = 60): Promise<void> {
    if (!this.api || !this.state || this.busy) return
    if (targets.includes(this.state.time_band)) return
    this.busy = true
    this.overlay?.setStatus('Advancing time to the dinner window...')
    try {
      for (let i = 0; i < maxSteps; i += 1) {
        if (!this.state || targets.includes(this.state.time_band)) break
        const out = await this.api.playerAction({ kind: 'daily_tick', n: 1 })
        this.applyActionResult(out)
        if (!out.ok) break
      }
      await this.refreshStoryEventsOnly()
    } finally {
      this.busy = false
    }
  }

  private async runPlayerAction(body: PlayerActionBody, successMessage: string): Promise<PlayerActionResult | null> {
    if (!this.api || this.busy) return null
    this.busy = true
    try {
      const out = await this.api.playerAction(body)
      this.applyActionResult(out)
      this.overlay?.setStatus(out.ok ? successMessage : `Action failed: ${out.error || 'unknown'}`)
      await this.refreshStoryEventsOnly()
      return out
    } finally {
      this.busy = false
    }
  }

  private applyActionResult(result: PlayerActionResult): void {
    if (!this.map || !this.renderer) return
    this.state = result.state
    this.renderer.render(this.map, this.state, this.storyEvents)
    this.overlay?.setContext(this.state, this.storyEvents, this.availableActivitiesForCurrentScene())
  }

  private applyStoryResult(result: StoryChooseResult): void {
    if (!this.map || !this.renderer || !result.state) return
    this.state = result.state
    if (result.available_events) this.storyEvents = result.available_events
    this.renderer.render(this.map, this.state, this.storyEvents)
    this.overlay?.setContext(this.state, this.storyEvents, this.availableActivitiesForCurrentScene())
  }

  private async refreshStoryEventsOnly(): Promise<void> {
    if (!this.api || !this.state || !this.map) return
    const story = await this.api.getAvailableStoryEvents()
    this.storyEvents = story.events || []
    this.state = story.state || this.state
    this.renderer?.render(this.map, this.state, this.storyEvents)
    this.overlay?.setContext(this.state, this.storyEvents, this.availableActivitiesForCurrentScene())
  }

  private availableActivitiesForCurrentScene(): SceneActivity[] {
    const sceneId = this.state?.player?.scene_id
    const timeBand = this.state?.time_band
    return this.sceneActivities.filter((item) => {
      const scenes = item.scene_ids?.length ? item.scene_ids : item.scene_id ? [item.scene_id] : []
      const timeBands = item.time_bands || []
      return (!scenes.length || scenes.includes(String(sceneId))) && (!timeBands.length || timeBands.includes(timeBand!))
    })
  }

  private nearestNpc(): AgentState | null {
    const player = this.state?.player
    if (!player) return null
    const sameMap = (this.state?.agents || []).filter((agent) => agent.map_id === player.map_id)
    sameMap.sort((a, b) => {
      const da = Math.abs(a.tile_x - player.tile_x) + Math.abs(a.tile_y - player.tile_y)
      const db = Math.abs(b.tile_x - player.tile_x) + Math.abs(b.tile_y - player.tile_y)
      return da - db
    })
    return sameMap[0] || null
  }

  private ensureRuntimeWiring(): void {
    if (!this.renderer) {
      const mapRoot = new Node('AutoMapRoot')
      mapRoot.setPosition(new Vec3(-430, 250, 0))
      this.node.addChild(mapRoot)
      this.renderer = mapRoot.addComponent(MapRenderer)

      const graphicsNode = new Node('MapGraphics')
      mapRoot.addChild(graphicsNode)
      this.renderer.mapGraphics = graphicsNode.addComponent(Graphics)

      const playerNode = new Node('Player')
      playerNode.addComponent(UITransform).setContentSize(64, 28)
      const playerLabel = playerNode.addComponent(Label)
      playerLabel.string = 'Player'
      playerLabel.fontSize = 16
      mapRoot.addChild(playerNode)
      this.renderer.playerNode = playerNode

      const npcRoot = new Node('NpcRoot')
      mapRoot.addChild(npcRoot)
      this.renderer.npcRoot = npcRoot

      const poiRoot = new Node('PoiRoot')
      mapRoot.addChild(poiRoot)
      this.renderer.poiRoot = poiRoot
    }

    if (!this.overlay) {
      const overlayNode = new Node('AutoOverlayUI')
      this.node.addChild(overlayNode)
      this.overlay = overlayNode.addComponent(OverlayUI)
      this.overlay.statusLabel = this.makeRuntimeLabel(overlayNode, 'StatusLabel', 'Starting Cocos v0...', -360, 300)
      this.overlay.objectiveLabel = this.makeRuntimeLabel(overlayNode, 'ObjectiveLabel', 'Syncing objectives...', -360, 266)
      this.overlay.detailLabel = this.makeRuntimeLabel(overlayNode, 'DetailLabel', 'Waiting for backend state...', -360, 232)
      this.makeRuntimeButton(overlayNode, 'RefreshButton', 'Refresh', 350, 300, () => this.refreshAll())
      this.makeRuntimeButton(overlayNode, 'StoryButton', 'Story', 350, 264, () => this.chooseFirstStoryChoice())
      this.makeRuntimeButton(overlayNode, 'ReadButton', 'Read', 350, 228, () => this.runReadingDemo())
      this.makeRuntimeButton(overlayNode, 'TrainButton', 'Train', 350, 192, () => this.runTrainingDemo())
      this.makeRuntimeButton(overlayNode, 'LunchButton', 'Lunch', 350, 156, () => this.runLunchDemo())
      this.makeRuntimeButton(overlayNode, 'DinnerButton', 'Dinner', 350, 120, () => this.runDinnerDemo())
      this.makeRuntimeButton(overlayNode, 'NpcProfileButton', 'NPC Profile', 350, 84, () => this.showNearestNpcProfile())
      this.makeRuntimeButton(overlayNode, 'GreetButton', 'Greet', 350, 48, () => this.greetNearestNpc())
      this.makeRuntimeButton(overlayNode, 'RestButton', 'Rest', 350, 12, () => this.restUntilNextDay())
      this.makeRuntimeButton(overlayNode, 'ResetButton', 'Reset', 350, -24, () => this.resetPrototype())
    }
  }

  private makeRuntimeLabel(parent: Node, name: string, text: string, x: number, y: number): Label {
    const node = new Node(name)
    parent.addChild(node)
    node.addComponent(UITransform).setContentSize(720, 32)
    node.setPosition(new Vec3(x, y, 0))
    const label = node.addComponent(Label)
    label.string = text
    label.fontSize = 18
    return label
  }

  private makeRuntimeButton(
    parent: Node,
    name: string,
    text: string,
    x: number,
    y: number,
    action: () => Promise<unknown> | void
  ): Button {
    const node = new Node(name)
    parent.addChild(node)
    node.addComponent(UITransform).setContentSize(150, 28)
    node.setPosition(new Vec3(x, y, 0))
    const label = node.addComponent(Label)
    label.string = text
    label.fontSize = 16
    const button = node.addComponent(Button)
    button.transition = Button.Transition.NONE
    node.on(Node.EventType.TOUCH_END, () => {
      void action()
    }, this)
    this.runtimeButtonNodes.push(node)
    return button
  }

  private isRuntimeButtonHit(location: { x: number; y: number }): boolean {
    return this.runtimeButtonNodes.some((node) => {
      const transform = node.getComponent(UITransform)
      if (!transform) return false
      const size = transform.contentSize
      const pos = node.worldPosition
      const halfWidth = size.width / 2
      const halfHeight = size.height / 2
      return (
        location.x >= pos.x - halfWidth &&
        location.x <= pos.x + halfWidth &&
        location.y >= pos.y - halfHeight &&
        location.y <= pos.y + halfHeight
      )
    })
  }

  private playLocalPath(path: Array<{ x: number; y: number }>): Promise<void> {
    const map = this.map
    const renderer = this.renderer
    const playerNode = renderer?.playerNode
    if (!map || !renderer || !playerNode) return Promise.resolve()
    const points = path.map((p) => renderer.tileToWorld(map, p.x, p.y))
    return new Promise((resolve) => {
      let chain = tween(playerNode)
      for (const p of points.slice(1)) chain = chain.to(0.08, { position: p })
      chain.call(() => resolve()).start()
    })
  }
}
