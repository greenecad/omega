import Phaser from './lib/phaser.js';
import { SCENE_KEYS } from './common/scene-keys.js';
import { FinalScene } from './scenes/final-scene.js';
import { PreloadScene } from './scenes/preload-scene.js';


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
      debug: false
    }
  },
  backgroundColor: '#000000',
};

const game = new Phaser.Game(gameConfig);
window.scene = SCENE_KEYS.LAST_SCENE; // set in global scope so that we can decide which scene to start in the preload scene based on the url query params

game.scene.add(SCENE_KEYS.PRELOAD_SCENE, PreloadScene);
game.scene.add(SCENE_KEYS.LAST_SCENE, FinalScene);
game.scene.start(SCENE_KEYS.PRELOAD_SCENE);
