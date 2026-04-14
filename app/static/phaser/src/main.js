import Phaser from './lib/phaser.js';
import { SCENE_KEYS } from './common/scene-keys.js';
import { GameScene } from './scenes/game-scene.js';
import { PreloadScene } from './scenes/preload-scene.js';

/** @type {Phaser.Types.Core.GameConfig} */
const gameConfig = {
  type: Phaser.CANVAS,
  pixelArt: true,
  roundPixels: true,
  scale: {
    parent: 'game-container',
    width: 640,
    height: 480,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    mode: Phaser.Scale.FIT,
  },
  physics: {
    default: 'arcade',
    arcade: {
      debug: true,
      gravity: { y: 300, x:0 }
    }
  },
  backgroundColor: '#000000',
};

const game = new Phaser.Game(gameConfig);

game.scene.add(SCENE_KEYS.PRELOAD_SCENE, PreloadScene);
game.scene.add(SCENE_KEYS.GAME_SCENE, GameScene);
game.scene.start(SCENE_KEYS.PRELOAD_SCENE);
