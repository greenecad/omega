import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from '../common/scene-keys.js';
import { ASSET_KEYS } from '../common/assets.js';

export class FightScene extends Phaser.Scene {
  constructor() {
    super(SCENE_KEYS.FIGHT_SCENE);
  }
  create() {
    window.scene = this
    this.genAnims();
    this.trail = this.add.rectangle(420, 260, 5, 20, 0xffffff).setOrigin(0.5, 0).setAlpha(0);
    this.thing = this.add.sprite(420, 260, ASSET_KEYS.THING).setAlpha(0)
    this.thing.hp = 8
    this.thing.on('animationcomplete', ()=>{

    })
    this.thing.anims.play('thing_0');
    this.time.delayedCall(
        2000,
        ()=>{
            window.scene.cameras.main.shake(800, .01)
        }
    )
    this.tweens.add({
        targets: [this.trail, this.thing],
        alpha: 1,
        duration: 1000,
        ease: 'Linear',
        repeat: 0,
        onComplete(){
            if (determination){
                window.scene.text= window.scene.add.text(420, 420, "You are filled with a sense of DETERMINATION.", {fontSize: 20}).setOrigin(.5, .5)
                window.scene.time.delayedCall(
                    2000,
                    ()=>{
                        window.scene.text.destroy()
                        this.hurtThing(2)
                    }
                )
            }
        }
    })
  }
  update() {
    this.trail.height += .1;
  }

  hurtThing(val=0){
    this.thing.hp-=val
    if (this.thing.hp>6){
        this.thing.anims.play("thing_hurt_0")
        this.time.delayedCall(1000, ()=>{
            this.thing?.anims.play("thing_0")
        })
    }
    else if (this.thing.hp>4){
        this.thing.anims.play("thing_hurt_1")
        this.time.delayedCall(1000, ()=>{
            this.thing?.anims.play("thing_1")
        })
    }
    else if (this.thing.hp>2){
        this.thing.anims.play("thing_hurt_2")
        this.time.delayedCall(1000, ()=>{
            this.thing?.anims.play("thing_2")
        })
    }
    else if (this.thing.hp>0){
        this.thing.anims.play("thing_hurt_3")
        this.time.delayedCall(1000, ()=>{
            this.thing?.anims.play("thing_3")
        })
    }
    else{
        this.thing.anims.play("thing_death")
        this.time.delayedCall(2000, ()=>{
           this.thing?.destroy();
        })
    }
  }
  genAnims() {
    this.anims.create({
      key: 'target_idle',
      frames: this.anims.generateFrameNumbers(ASSET_KEYS.TARGET2, { start: 0, end: 1 }),
      frameRate: 2,
      repeat: -1
    });
    this.anims.create({
        key: 'thing_0',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 0, end: 1 }),
        frameRate: 2,
        repeat: -1
    });
    this.anims.create({
        key: 'thing_hurt_0',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 2, end: 2 }),
        frameRate: 1,
        repeat: 0
    });
    this.anims.create({
        key: 'thing_1',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 3, end: 4 }),
        frameRate: 2,
        repeat: -1
    });
    this.anims.create({
        key: 'thing_hurt_1',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 5, end: 5 }),
        frameRate: 1,
        repeat: 0
    });
    this.anims.create({
        key: 'thing_2',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 6, end: 7 }),
        frameRate: 2,
        repeat: -1
    });
    this.anims.create({
        key: 'thing_hurt_2',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 8, end: 8 }),
        frameRate: 1,
        repeat: 0
    });
    this.anims.create({
        key: 'thing_3',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 9, end: 10 }),
        frameRate: 2,
        repeat: -1
    });
    this.anims.create({
        key: 'thing_hurt_3',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 11, end: 11 }),
        frameRate: 1,
        repeat: 0
    });
    this.anims.create({
        key: 'thing_death',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 12, end: 15 }),
        frameRate: 2,
        repeat: 0
    });
  }
}

