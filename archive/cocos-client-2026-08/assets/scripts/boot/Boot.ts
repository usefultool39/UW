import { _decorator, Component, director } from 'cc'
import { CLIENT_CONTRACT_VERSION } from '../api/contracts'

const { ccclass, property } = _decorator

@ccclass('Boot')
export class Boot extends Component {
  @property
  nextScene = 'Field'

  onLoad(): void {
    console.info(`Border Echo Cocos boot: ${CLIENT_CONTRACT_VERSION}`)
  }

  start(): void {
    if (this.nextScene) director.loadScene(this.nextScene)
  }
}

