import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from '../common/scene-keys.js';
import { ASSET_KEYS } from '../common/assets.js';
class CloudPlatform extends Phaser.Physics.Arcade.Sprite {
  constructor(scene, x, y, texture, group) {
    super(scene, x, y, texture);
    this.scene = scene;
    scene.add.existing(this);
    scene.physics.add.existing(this);  
    this.setOrigin(0);
    this.vx;
    this.vy;
    this.previousX = this.x;
    this.previousY = this.y;
 //   this.playerLocked = false;
    group.add(this);
 
    this.body.customSeparateX = true;// these 2 lines of code should come after the group.add 
    this.body.customSeparateY = true;// since properties will be overwritten by the group defaults
  }
  
  addMotionPath(motionPath) {  
    this.tweenX = this.scene.tweens.createTimeline({
      loop: -1,
      onUpdate: (tween, target) => {
        this.vx = this.body.position.x - this.previousX;
        this.previousX = this.body.position.x;     
      }
    });

    this.tweenY = this.scene.tweens.createTimeline({
      loop: -1,
      onUpdate: (tween, target) => {        
        this.vy = this.body.position.y - this.previousY;    
        this.previousY = this.body.position.y; 
      }
    });
    
    var destX = this.x;
    var destY = this.y;
    for (var i = 0; i<motionPath.length; i++) {
      destX += Number(motionPath[i].x);
      destY += Number(motionPath[i].y);
      this.tweenX.add({targets: this, x: destX, duration: motionPath[i].xSpeed, ease: motionPath[i].xEase})
      this.tweenY.add({targets: this, y: destY, duration: motionPath[i].ySpeed, ease: motionPath[i].yEase})
    }
   return this
  }
  
  start() {
    this.tweenX.play();
    this.tweenY.play();
  }
  
  stop() {
    this.tweenX.stop();
    this.tweenY.stop();
  }
}

class Player extends Phaser.Physics.Arcade.Sprite {
  constructor(scene, x, y) {
    super(scene, x, y, ASSET_KEYS.PLAYER);
    this.scene = scene;
    scene.add.existing(this);
    scene.physics.add.existing(this);
    this.setCollideWorldBounds(true);
    //this.body.setSize(20, 32).setOffset(6,16);
    this.setScale(0.5);
    this.facing = 'left';
    this.jumpTimer = 0;     
    this.locked = false;
    this.lockedTo = null;
    this.wasLocked = false;
    this.willJump = false;
    this.cursors = this.scene.input.keyboard.createCursorKeys();
  } 

  update(time) {

    this.body.setVelocityX(0); 
    
    if (this.cursors.left.isDown) {
      this.body.setVelocityX(-200);
      this.anims.play('move', true);
      this.setFlipX(true);
      this.facing = 'left'; 
    } else if (this.cursors.right.isDown) { 
      this.body.setVelocityX(200);
      this.anims.play('move', true);
      this.setFlipX(false);
      this.facing = 'right';  
    } else {
      if (this.facing !== 'idle') {
        this.anims.play('idle', true);
        this.facing = 'idle';
      }
    }
  
    var standing = this.body.blocked.down || this.body.touching.down;
    if ((standing && this.cursors.up.isDown && time > this.jumpTimer) ||
        (this.cursors.up.isDown && this.locked && time > this.jumpTimer)) {
      if (this.locked) {
        this.cancelLock();
      }
      this.willJump = true;
    }

    if (this.locked) {
      this.checkLock();
    }
   
  }
 
  checkLock() {
    this.body.velocity.y = 0;
    //  If the player has walked off either side of the platform then they're no longer locked to it
    if (this.body.right < this.lockedTo.body.x || this.body.x > this.lockedTo.body.right) {
      this.cancelLock();
    }

  }

  cancelLock() {
    this.wasLocked = true;
    this.locked = false;
  }

  // in the original Phaser 2 version, this bit of the code is included in preRender loop of main game scene
  preRender(time) {
  
    if (this.locked || this.wasLocked) {
     this.body.position.x += this.lockedTo.vx;
  //   this.body.position.y += this.lockedTo.vy;
     this.body.y = this.lockedTo.body.y - this.body.height; 
//      this.y = this.lockedTo.y - 48/2;
    }

    if (this.willJump) {
   
      this.willJump = false;
      if (this.lockedTo && this.lockedTo.vy < 0 && this.wasLocked) {
        //  If the platform is moving up we add its velocity to the players jump
        this.body.velocity.y = -300 + (this.lockedTo.vy * 10);
      } else
      {
        this.body.velocity.y = -300;
      }
      this.jumpTimer = time + 750;
    }

    if (this.wasLocked) {
      this.wasLocked = false;
    //  this.lockedTo.playerLocked = false;
      this.lockedTo = null;     
    }
  }
}


export class GameScene extends Phaser.Scene {
  constructor() {
    super({
      key: SCENE_KEYS.GAME_SCENE,
    });
  }

  /**
   * @public
   * Tied to the Phaser Scene lifecycle. Will run one time after the PRELOAD
   * logic is finished. Runs each time the Phaser Scene restarts.
   * @returns {void}
   */
  create() {
    // show image we loaded in the preload scene
    this.player = new Player(this, this.scale.width / 2, this.scale.height / 2);
    this.genAnims();
    this.player.play('idle');
  }
  update(){
    this.player.update(this.time.now);
  }
  genAnims(){
    this.anims.create({
      key: 'idle',
      frames: this.anims.generateFrameNumbers(ASSET_KEYS.PLAYER, { start: 0, end: 1 }),
      frameRate: 2,
      repeat: -1
    });
    this.anims.create({
      key: 'move',
      frames: this.anims.generateFrameNumbers(ASSET_KEYS.PLAYER, { start: 2, end: 3 }),
      frameRate: 2,
      repeat: -1
    });
  }
}
