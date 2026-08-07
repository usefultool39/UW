import { _decorator, Component, Label } from 'cc'
import { SceneActivity, StoryEvent, WorldState } from '../api/contracts'

const { ccclass, property } = _decorator

@ccclass('OverlayUI')
export class OverlayUI extends Component {
  @property(Label)
  statusLabel: Label | null = null

  @property(Label)
  objectiveLabel: Label | null = null

  @property(Label)
  detailLabel: Label | null = null

  setStatus(text: string): void {
    if (this.statusLabel) this.statusLabel.string = text
  }

  setContext(state: WorldState, storyEvents: StoryEvent[], activities: SceneActivity[]): void {
    if (this.objectiveLabel) {
      const eventTitle = storyEvents[0]?.title || 'Free explore'
      this.objectiveLabel.string = `Day ${state.day} | ${state.time_band} | ${eventTitle}`
    }
    if (this.detailLabel) {
      const activityNames = activities.slice(0, 3).map((item) => item.label || item.title).join(' / ')
      this.detailLabel.string = activityNames || 'Move near the library, great tree, or hearth to run daily actions.'
    }
  }
}
