import Phaser from './lib/phaser.js';
import { SCENE_KEYS } from './common/scene-keys.js';
import { PreloadScene } from './scenes/preload-scene.js';
import { FightScene } from './scenes/fight-scene.js';

/** @type {Phaser.Types.Core.GameConfig} */
const gameConfig = {
  type: Phaser.CANVAS,
  pixelArt: true,
  roundPixels: true,
  scale: {
    parent: 'game-container',
    width: 840,
    height: 680,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    mode: Phaser.Scale.FIT,
  },
  physics: {
    default: 'arcade',
    arcade: {
      debug: true,
    }
  },
  backgroundColor: '#000000',
};

window.scene = SCENE_KEYS.FIGHT_SCENE; // set in global scope so that we can decide which scene to start in the preload scene based on the url query params
const game = new Phaser.Game(gameConfig);

game.scene.add(SCENE_KEYS.PRELOAD_SCENE, PreloadScene);
game.scene.add(SCENE_KEYS.FIGHT_SCENE, FightScene);
game.scene.start(SCENE_KEYS.PRELOAD_SCENE);