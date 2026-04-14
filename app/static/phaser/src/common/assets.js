export const ASSET_KEYS = Object.freeze({
  LOGO: 'LOGO',
  PLAYER: 'PLAYER',
});

export const IMAGE_ASSETS = [
  {
    assetKey: ASSET_KEYS.LOGO,
    path: 'static/phaser/assets/images/logo.png',
  },
  {
    assetKey: ASSET_KEYS.PLAYER,
    path: 'static/phaser/assets/images/slime-16x8.png',
    spritesheet: {
      width: 128,
      height: 128
    }

  }
];
