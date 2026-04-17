import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from '../common/scene-keys.js';
import { ASSET_KEYS } from '../common/assets.js';
//let time_elapsed
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
    this.tweenX = this.scene.tweens.add({
      targets: this,
      loop: -1,
      onUpdate: (tween, target) => {
        this.vx = this.body.position.x - this.previousX;
        this.previousX = this.body.position.x;     
      },
      onComplete: (tween, target) => {
        this.destroy();
      }

    });

    this.tweenY = this.scene.tweens.add({
      targets: this,
      loop: -1,
      onUpdate: (tween, target) => {        
        this.vy = this.body.position.y - this.previousY;    
        this.previousY = this.body.position.y; 
      },
      onComplete: (tween, target) => {
        this.destroy();
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
    this.setScale(0.3);
    this.facing = 'left';    
    this.locked = false;
    this.lockedTo = null;
    this.wasLocked = false;
    this.willJump = false;
    this.cursors = this.scene.input.keyboard.createCursorKeys();
  } 
 
  update(time) {

    this.body.setVelocityX(0); 
    
    if (this.cursors.left.isDown) {
      this.body.setVelocityX(-400);
      this.anims.play('move', true);
      this.setFlipX(true);
      this.facing = 'left'; 
    } else if (this.cursors.right.isDown) { 
      this.body.setVelocityX(400);
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
    if ((standing && this.cursors.up.isDown) ||
        (this.cursors.up.isDown && this.locked )) {
      if (this.locked) {
        this.cancelLock();
      }
      this.willJump = true;
    }
    if (!standing && !this.cursors.up.isDown && this.body.velocity.y < 0) {
      this.body.velocity.y = 0;
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
      this.body.velocity.y = -700;
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
  customSep(player, platform) {
   //     if (platform.body.touching.up && player.body.touching.down) {
    if (!player.locked && player.body.velocity.y > 0) {
      player.locked = true;
      player.lockedTo = platform;
  //    platform.playerLocked = true;
      player.body.velocity.y = 0;
    }
    
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
    this.platforms =this.physics.add.group({
      immovable: true,
      allowGravity: false
    });
    this.killPlatform = this.physics.add.staticSprite(0, 578, ASSET_KEYS.PLATFORM_LONG).setScale(5).setOrigin(0, 0);
    this.killPlatform.refreshBody();
    this.physics.add.collider(this.player, this.killPlatform, () => {
      //this.player.destroy();
      this.scene.pause();
      const submitButton = document.getElementById('submit-button');
      if (submitButton) {
        submitButton.style.display = 'block';
      }
    });
    let key;
    if (determination){
      key= ASSET_KEYS.PLATFORM_LONG;
    }
    else{
      key= ASSET_KEYS.PLATFORM_SHORT;
    }
    var startPlatform = new CloudPlatform(this, 300, 450, key, this.platforms);
    //startPlatform.setScale(5);
    this.tweens.add({
      targets: startPlatform,
      x: -800,
      duration: 8000,
      onUpdate: (tween, target) => {
        target.vx = target.body.position.x - target.previousX;
        target.previousX = target.body.position.x;     
      },
      onComplete: () => {
        startPlatform.destroy();
      }
    })
    /*startPlatform.addMotionPath([
      { x: "+0", xSpeed: 2000, xEase: "Linear", y: "+300", ySpeed: 2000, yEase: "Sine.easeIn" },
      { x: "-0", xSpeed: 2000, xEase: "Linear", y: "-300", ySpeed: 2000, yEase: "Sine.easeOut" }
    ]).start();*/
    var time = 6000;
    this.physics.add.collider(this.player, this.platforms, this.customSep, null, this);
    var delay = 2500;
    this.time.addEvent({
      delay: delay,
      callback: () => {
        var y = Phaser.Math.Between(200, 500);
        var platform = new CloudPlatform(this, 800, y, key, this.platforms);
        platform.setScale(.12);
        if (determination){
          platform.setScale(.15);
        }
        this.tweens.add({
          targets: platform,
          x: -200,
          duration: time,
          onUpdate: (tween, target) => {
            target.vx = target.body.position.x - target.previousX;
            target.previousX = target.body.position.x;     
          },
          onComplete: () => {
            platform.destroy();
            if (time > 1000) {
              time -= 55;
              delay -= 20;
            }
          }
        });
      },
      loop: true
    });
    window.time_elapsed = 0;
    this.time_text = this.add.text(10, 10, 'Time: 0', { font: '20px Arial', fill: '#ffffff' });
    this.score_text = this.add.text(10, 40, 'Score: 0', { font: '20px Arial', fill: '#ffffff' }); 
    if(determination)
      this.add.text(10, 60, 'you feel a sense of DETERMINATION.', { font: '20px Arial', fill: '#ffffff' });
  }
  update(){
    this.player.update(this.time.now);
    this.player.preRender(this.time.now);
    window.time_elapsed += this.game.loop.delta;
    this.time_text.setText('Time: ' + Math.floor(window.time_elapsed / 1000));
    this.score_text?.setText('Score: ' + Math.floor(Math.floor(window.time_elapsed / 1000) / 10)*10);
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

let submitScore = () => {
  let seconds = Math.floor(window.time_elapsed / 1000);
  let score = Math.floor(seconds / 10)*10;
  console.log('Submitting score:', score);
  document.getElementById("score-input").value = score;
  document.getElementById("score-form").submit();
}

// Make it available globally for the onclick handler
window.submitScore = submitScore;