import { AGENTS } from './gameContentConfig.js'
import { DEFAULT_MAP_ID, getWorldBackgroundAsset } from './sceneRegistry.js'

export const GAME_ASSET_PATHS = {
  worldBackground: getWorldBackgroundAsset(DEFAULT_MAP_ID),
  playerToken: AGENTS.player.asset,
  aliceToken: AGENTS.alice.asset,
  eugeoToken: AGENTS.eugeo.asset
}
