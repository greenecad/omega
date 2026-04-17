export const ASSET_KEYS = Object.freeze({
  PLAYER: 'PLAYER',
  PLATFORM_SHORT: 'PLATFORM_SHORT',
  PLATFORM_LONG: 'PLATFORM_LONG',
  TARGET: 'TARGET'
});

export const IMAGE_ASSETS = [
  {
    assetKey: ASSET_KEYS.PLAYER,
    path: 'static/phaser/assets/images/slime-16x8.png',
    spritesheet: {
      width: 128,
      height: 128
    }

  },
  {
    assetKey: ASSET_KEYS.PLATFORM_SHORT,
    path: 'static/phaser/assets/images/platform-short.png'
  },
  {
    assetKey: ASSET_KEYS.PLATFORM_LONG,
    path: 'static/phaser/assets/images/platform-long.png'

  },
  {
    assetKey: ASSET_KEYS.TARGET,
    path: 'static/phaser/assets/images/target.png'
  }
];
