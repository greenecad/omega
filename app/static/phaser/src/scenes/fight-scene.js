import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from '../common/scene-keys.js';
import { ASSET_KEYS } from '../common/assets.js';

export class FightScene extends Phaser.Scene {
  constructor() {
    super(SCENE_KEYS.FIGHT_SCENE);
  }
  create() {
    window.scene = this
    this.started = false;
    this.delay = true;
    this.won= false;
    this.genAnims();
    this.targets = this.physics.add.group();
    this.startTarget = this.physics.add.sprite(520, 230, ASSET_KEYS.TARGET2)
    this.startTarget.anims.play('target_idle');
    this.startTarget.setInteractive();
    this.startTarget.on('pointerdown', ()=>{
        this.time.delayedCall(1000, ()=>{
            this.trail = this.add.rectangle(520, 230, 5, 40, 0xff0000).setOrigin(0.5, 0).setAlpha(0);
            this.thing = this.physics.add.staticSprite(520, 230, ASSET_KEYS.THING).setAlpha(0)
            this.thing.hp = 8
            
            this.physics.add.collider(this.thing, this.targets, (thing, target)=>{
                if(!target.postSpawn){
                    target.x = Phaser.Math.Between(50, 990);
                    target.y = Phaser.Math.Between(30, 590);
                }
            })

            this.thing.anims.play('thing_0');
            this.time.delayedCall(
                1000,
                ()=>{
                    window.scene.sound.play(ASSET_KEYS.CRY1);
                    window.scene.cameras.main.shake(6000, .01)
                    
                }
            )
            this.time.delayedCall(
                7000,
                ()=>{
                    window.scene.createTargets(0)
                    this.started = true
                    window.scene.music=  window.scene.sound.add(ASSET_KEYS.MUSIC, {loop: true});
                    window.scene.music.play()
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
                        window.scene.text= window.scene.add.text(520, 420, "You are filled with a sense of DETERMINATION.", {fontSize: 20}).setOrigin(.5, .5)
                        window.scene.time.delayedCall(
                            1500,
                            ()=>{
                                window.scene.text.destroy()
                                window.scene.hurtThing(2)
                            }
                        )
                    }
                }
            })
        })
        this.startTarget.destroy();
        
    })
    
    this.resetText = this.add.text(530, 640, "GO BACK", {fontSize: 30}).setOrigin(.5,.5)
    this.resetText.setInteractive();
    this.resetText.on("pointerup", ()=>{
        this.endFight();
    })
    
  }
  update() {
    if(this.trail && !this.won && this.started){
        this.trail.height += .11;
        if (this.trail.height >= 425 && !this.won){
            this.endFight()
        }
    }
    if(this.targets.children.size == 0 && this.started && this.delay && !this.won){
        this.delay=false
        this.time.delayedCall(200, ()=>{
            this.hurtThing(1);
        })
        this.time.delayedCall(1200, ()=>{
            if(this.thing.hp>0)
                this.createTargets(8-this.thing.hp)
            this.delay = true
        })
    }
  }
  createTargets(phase){
    let count = 5 + phase;
    for(let i = 0; i< count; i++){
        let x = Phaser.Math.Between(50, 990);
        let y = Phaser.Math.Between(30, 590);
        let target= this.targets.create(x, y, ASSET_KEYS.TARGET2);
        target.postSpawn= false
        this.time.delayedCall(50, ()=>{
            target.postSpawn=true;
        })
        target.anims.play("target_idle");
        target.setInteractive().setScale(.2);
        target.on('pointerdown', ()=>{
            target.destroy();
        })
        if(this.thing.hp<3){
            target.setCollideWorldBounds(true, 1, 1, true);
            target.setVelocityX(Phaser.Math.Between(-100, 100))
            target.setVelocityY(Phaser.Math.Between(-100, 100))
        }
    }
  }

  hurtThing(val=0){
    this.thing.hp-=val
    this.sound.play(ASSET_KEYS.CRY2)
    this.cameras.main.shake(200, .005)
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
        this.won = true;
        this.cameras.main.shake(800, .15)
        this.tweens.add({
            targets: this.trail,
            alpha: 0,
            duration: 200,
            onComplete(){
                window.scene.trail.destroy();
            }
        })
        this.time.delayedCall(2000, ()=>{
           this.thing?.destroy();
           
           this.win();
        })
    }
  }
  endFight(){
    window.location.href= "https://chsomegachallenge.com/profile"
  }
  win(){
    this.won = true;
    this.music.stop();
    this.scene.pause(SCENE_KEYS.FIGHT_SCENE);
    let windiv= document.getElementById('complete')
    if(windiv){
        windiv.style.display = 'block';
    }
    let code = document.getElementById('code')
    if(code){
        code.innerText = "[[aaaaa aaabb baaaa aabaa aaaaa ababb babba abbab baabb aabaa aabbb aaaaa aaabb aaaab aabaa aabab abbab baaaa aabaa]]"
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
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 4, end: 5 }),
        frameRate: 2,
        repeat: -1
    });
    this.anims.create({
        key: 'thing_hurt_1',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 3, end: 3 }),
        frameRate: 1,
        repeat: 0
    });
    this.anims.create({
        key: 'thing_2',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 7, end: 8 }),
        frameRate: 2,
        repeat: -1
    });
    this.anims.create({
        key: 'thing_hurt_2',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 6, end: 6 }),
        frameRate: 1,
        repeat: 0
    });
    this.anims.create({
        key: 'thing_3',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 10, end: 11 }),
        frameRate: 2,
        repeat: -1
    });
    this.anims.create({
        key: 'thing_hurt_3',
        frames: this.anims.generateFrameNumbers(ASSET_KEYS.THING, { start: 9, end: 9 }),
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

