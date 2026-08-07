import {
  ApiRoutes,
  DEFAULT_API_BASE,
  DEFAULT_WORLD_MAP_ID,
  DialogueResult,
  MapData,
  NpcProfile,
  PlayerActionBody,
  PlayerActionResult,
  SaveData,
  SceneActivity,
  StoryChooseResult,
  StoryEvent,
  WorldState
} from './contracts'

export class GameApi {
  constructor(private readonly baseUrl: string = DEFAULT_API_BASE) {}

  async getState(): Promise<WorldState> {
    return this.getJson<WorldState>(ApiRoutes.state)
  }

  async getWorldMap(mapId = DEFAULT_WORLD_MAP_ID): Promise<MapData> {
    const route = mapId === DEFAULT_WORLD_MAP_ID ? ApiRoutes.worldMap : ApiRoutes.worldMapById(mapId)
    return this.getJson<MapData>(route)
  }

  async getAvailableStoryEvents(): Promise<{ ok: boolean; events: StoryEvent[]; state: WorldState }> {
    return this.getJson(ApiRoutes.availableStoryEvents)
  }

  async getSceneActivities(): Promise<{ v: number; activities: SceneActivity[] }> {
    return this.getJson(ApiRoutes.sceneActivities)
  }

  async playerAction(body: PlayerActionBody): Promise<PlayerActionResult> {
    return this.postJson<PlayerActionResult>(ApiRoutes.playerAction, body)
  }

  async chooseStoryEvent(eventId: string, choiceId: string): Promise<StoryChooseResult> {
    return this.postJson<StoryChooseResult>(ApiRoutes.storyChoose, {
      event_id: eventId,
      choice_id: choiceId
    })
  }

  async sendDialogue(npcId: string, message: string, context: Record<string, unknown> = {}): Promise<DialogueResult> {
    return this.postJson<DialogueResult>(ApiRoutes.dialogue, {
      npc_id: npcId,
      message,
      context
    })
  }

  async getNpcProfile(npcId: string): Promise<{ ok: boolean; profile: NpcProfile }> {
    return this.getJson(ApiRoutes.npcProfile(npcId))
  }

  async exportSave(): Promise<SaveData> {
    return this.getJson(ApiRoutes.saveExport)
  }

  async importSave(save: SaveData): Promise<{ ok: boolean; state: WorldState }> {
    return this.postJson(ApiRoutes.saveImport, save)
  }

  async reset(): Promise<{ ok: boolean; run_id: string; state: WorldState }> {
    return this.postJson(ApiRoutes.reset, {})
  }

  private async getJson<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`)
    return this.readResponse<T>(res)
  }

  private async postJson<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    return this.readResponse<T>(res)
  }

  private async readResponse<T>(res: Response): Promise<T> {
    let payload: unknown = null
    try {
      payload = await res.json()
    } catch {
      payload = null
    }
    if (!res.ok) {
      const message = typeof payload === 'object' && payload && 'detail' in payload
        ? String((payload as { detail?: unknown }).detail)
        : `HTTP ${res.status}`
      throw new Error(message)
    }
    return payload as T
  }
}
