import { _decorator, Color, Component, Graphics, Label, Node, UITransform, Vec3 } from 'cc'
import { AgentState, MapData, MapPoi, StoryEvent, WorldState } from '../api/contracts'
import { terrainCodeAt } from './LocalPath'

const { ccclass, property } = _decorator

const TERRAIN_COLORS: Record<number, Color> = {
  0: new Color(79, 133, 84, 255),
  1: new Color(45, 89, 61, 255),
  2: new Color(47, 119, 154, 255),
  3: new Color(150, 125, 76, 255),
  4: new Color(92, 73, 58, 255),
  5: new Color(120, 94, 67, 255),
  9: new Color(38, 47, 50, 255)
}

@ccclass('MapRenderer')
export class MapRenderer extends Component {
  @property(Graphics)
  mapGraphics: Graphics | null = null

  @property(Node)
  playerNode: Node | null = null

  @property(Node)
  npcRoot: Node | null = null

  @property(Node)
  poiRoot: Node | null = null

  private map: MapData | null = null

  render(map: MapData, state: WorldState, events: StoryEvent[]): void {
    this.map = map
    this.drawTerrain(map)
    this.placePlayer(map, state)
    this.placeAgents(map, state.agents || [])
    this.placePois(map, map.pois || [], events)
  }

  tileToWorld(map: MapData, x: number, y: number): Vec3 {
    const ts = map.tile_size
    return new Vec3((x + 0.5) * ts, -(y + 0.5) * ts, 0)
  }

  worldToTile(world: Vec3): { x: number; y: number } | null {
    if (!this.map) return null
    const ts = this.map.tile_size
    const x = Math.floor(world.x / ts)
    const y = Math.floor(-world.y / ts)
    if (x < 0 || y < 0 || x >= this.map.width || y >= this.map.height) return null
    return { x, y }
  }

  uiToTile(location: { x: number; y: number }): { x: number; y: number } | null {
    const origin = this.node.worldPosition
    return this.worldToTile(new Vec3(location.x - origin.x, location.y - origin.y, 0))
  }

  setPlayerTile(map: MapData, x: number, y: number): void {
    this.playerNode?.setPosition(this.tileToWorld(map, x, y))
  }

  private drawTerrain(map: MapData): void {
    const g = this.mapGraphics
    if (!g) return
    const ts = map.tile_size
    g.clear()
    for (let y = 0; y < map.height; y += 1) {
      for (let x = 0; x < map.width; x += 1) {
        const code = terrainCodeAt(map, x, y)
        g.fillColor = TERRAIN_COLORS[code] || TERRAIN_COLORS[0]
        g.rect(x * ts, -(y + 1) * ts, ts, ts)
        g.fill()
      }
    }
  }

  private placePlayer(map: MapData, state: WorldState): void {
    const p = state.player
    this.setPlayerTile(map, p.tile_x, p.tile_y)
  }

  private placeAgents(map: MapData, agents: AgentState[]): void {
    if (!this.npcRoot) return
    this.npcRoot.removeAllChildren()
    for (const agent of agents) {
      if (agent.map_id !== map.id) continue
      const node = new Node(agent.id)
      const label = node.addComponent(Label)
      label.string = agent.id
      label.fontSize = 16
      label.color = new Color(255, 247, 214, 255)
      node.addComponent(UITransform).setContentSize(64, 24)
      node.setPosition(this.tileToWorld(map, agent.tile_x, agent.tile_y))
      this.npcRoot.addChild(node)
    }
  }

  private placePois(map: MapData, pois: MapPoi[], events: StoryEvent[]): void {
    if (!this.poiRoot) return
    this.poiRoot.removeAllChildren()
    for (const poi of pois) this.addMarker(map, poi.tile_x, poi.tile_y, poi.label || poi.id)
    for (const event of events) {
      const loc = event.location
      if (typeof loc?.tile_x === 'number' && typeof loc?.tile_y === 'number') {
        this.addMarker(map, loc.tile_x, loc.tile_y, event.title || event.id)
      }
    }
  }

  private addMarker(map: MapData, x: number, y: number, text: string): void {
    if (!this.poiRoot) return
    const node = new Node(`marker:${text}`)
    const label = node.addComponent(Label)
    label.string = text
    label.fontSize = 12
    label.color = new Color(255, 222, 99, 255)
    node.addComponent(UITransform).setContentSize(120, 24)
    node.setPosition(this.tileToWorld(map, x, y))
    this.poiRoot.addChild(node)
  }
}
