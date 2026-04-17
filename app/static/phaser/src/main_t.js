import Phaser from './lib/phaser.js';
import { SCENE_KEYS } from './common/scene-keys.js';
import { PreloadScene } from './scenes/preload-scene.js';
import { TargetPracticeScene } from './scenes/target_practice.js';

/** @type {Phaser.Types.Core.GameConfig} */
const gameConfig = {
  type: Phaser.CANVAS,
  pixelArt: true,
  roundPixels: true,
  scale: {
    parent: 'game-container',
    width: 840,
    height: 580,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    mode: Phaser.Scale.FIT,
  },
  physics: {
    default: 'arcade',
    arcade: {
      debug: true,
    }
  },
  backgroundColor: '#101010',
};

window.scene = SCENE_KEYS.TARGET_PRACTICE_SCENE; // set in global scope so that we can decide which scene to start in the preload scene based on the url query params
const game = new Phaser.Game(gameConfig);

game.scene.add(SCENE_KEYS.PRELOAD_SCENE, PreloadScene);
game.scene.add(SCENE_KEYS.TARGET_PRACTICE_SCENE, TargetPracticeScene);
game.scene.start(SCENE_KEYS.PRELOAD_SCENE);