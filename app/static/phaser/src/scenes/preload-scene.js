import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from '../common/scene-keys.js';
import { IMAGE_ASSETS } from '../common/assets.js';

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super({
      key: SCENE_KEYS.PRELOAD_SCENE,
    });
  }

  preload() {
    IMAGE_ASSETS.forEach((asset) => {
      if(asset.spritesheet){
        this.load.spritesheet(asset.assetKey, asset.path, {
          frameWidth: asset.spritesheet.width,
          frameHeight: asset.spritesheet.height
        });
        return;
      }
      this.load.image(asset.assetKey, asset.path);
    });
  }

  create() {
    this.scene.start(SCENE_KEYS.GAME_SCENE);
  }
}
