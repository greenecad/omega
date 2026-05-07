export const ASSET_KEYS = Object.freeze({
  PLAYER: 'PLAYER',
  PLATFORM_SHORT: 'PLATFORM_SHORT',
  PLATFORM_LONG: 'PLATFORM_LONG',
  TARGET: 'TARGET',
  TARGET2: 'TARGET2',
  THING: 'THING',
  CRY1: 'CRY1',
  CRY2: 'CRY2',
  MUSIC: 'MUSIC',
  RHO: "RHO",
  GLITCH: "GLITCH",
  BTFL: "BTFL",
  VOICE_1:"VOICE_1"
});

export const IMAGE_ASSETS = [
  {
    assetKey: ASSET_KEYS.PLAYER,
    path: '/static/phaser/assets/images/slime-16x8.png',
    spritesheet: {
      width: 128,
      height: 128
    }

  },
  {
    assetKey: ASSET_KEYS.PLATFORM_SHORT,
    path: '/static/phaser/assets/images/platform-short.png'
  },
  {
    assetKey: ASSET_KEYS.PLATFORM_LONG,
    path: '/static/phaser/assets/images/platform-long.png'

  },
  {
    assetKey: ASSET_KEYS.TARGET,
    path: '/static/phaser/assets/images/target.png'
  },
  {
    assetKey: ASSET_KEYS.TARGET2,
    path: '/static/phaser/assets/images/target-2.png',
    spritesheet:{
      width: 175,
            height: 175
    }
  },
  {
    assetKey: ASSET_KEYS.THING,
    path: '/static/phaser/assets/images/thing.png',
    spritesheet:{
      width: 224,
      height: 224
    }
  },
  {
    assetKey: ASSET_KEYS.CRY1,
    path: '/static/phaser/assets/images/cry1.mp3',
    audio: true
  },
  {
    assetKey: ASSET_KEYS.CRY2,
    path: '/static/phaser/assets/images/cry2.mp3',
    audio: true
  },
  {
    assetKey: ASSET_KEYS.MUSIC,
    path: '/static/phaser/assets/images/WOTW.mp3',
    audio: true
  },
  {
    assetKey: ASSET_KEYS.RHO,
    path: '/static/phaser/assets/images/rho.png'
  },
  {
    assetKey: ASSET_KEYS.BTFL,
    path: '/static/phaser/assets/images/BTFL.mp3',
    audio: true
  },
  {
    assetKey: ASSET_KEYS.VOICE_1,
    path: '/static/phaser/assets/images/talk1.wav',
    audio: true
  }
];
