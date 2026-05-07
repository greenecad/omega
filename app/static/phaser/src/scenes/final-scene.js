import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from '../common/scene-keys.js';
import { ASSET_KEYS } from '../common/assets.js';

export class FinalScene extends Phaser.Scene {
  constructor() {
    super(SCENE_KEYS.LAST_SCENE);
  }
  create(){
    window.scene=this
    this.started = false
    this.rho = this.add.sprite(420, 280, ASSET_KEYS.RHO).setAlpha(0).setScale(.20);
    this.tweens.add({
        targets: this.rho,
        y: 320,
        ease: 'Sine.easeInOut',
        repeat: -1, 
        yoyo: true,
        duration: 5000
    })
    this.input.keyboard.enabled = true;
    this.input.keyboard.on('keyup-C', this.endCountdown)
    this.input.on('pointerdown', ()=>{
        if (!this.started){
            this.started = true
            let speech = this.sound.add(ASSET_KEYS.VOICE_1)
            speech.on('complete', this.startCountdown)
            let glitch = this.sound.add(ASSET_KEYS.GLITCHSOUND, {loop: false})
            glitch.once('complete', ()=>{
                glitch.stop()
                speech.play()
            })
            glitch.play()
            this.tweens.add({
                targets: this.rho,
                alpha: 1,
                ease: 'Sine.easeIn',
                repeat: 0,
                onComplete: ()=>{
                    
                }
            })
        }
    })

  }

  startCountdown(){
    window.scene.time.delayedCall(1000, ()=>{
        window.scene.timer = window.scene.add.text(420, 535, "15:00", {fontSize: 80}).setOrigin(.5, .5)
        window.scene.time_count = 900
        window.scene.music = window.scene.sound.add(ASSET_KEYS.BTFL, {loop: true})
        window.scene.music.play()
        window.scene.countdown1 = window.scene.time.addEvent({
            delay:1200,
            callback: ()=>{
                if(window.scene.time_count < 60){
                    window.scene.time_count-=.5
                }
                else{
                    window.scene.time_count-=1
                }
                
                let minutes = (Math.floor(window.scene.time_count / 60)).toString()
                let seconds_num = Math.floor(window.scene.time_count % 60)
                let seconds =seconds_num.toString()
                if (seconds_num<10){
                    seconds = "0" + seconds_num.toString()
                }
                window.scene.timer.setText(minutes + ":"+seconds)
            },
            loop: true
        })
    })
    
  }
  endCountdown(){
    console.log('b')
    if(window.scene.started){
        window.scene.countdown1.destroy()
        window.scene.timer.destroy()
        window.scene.cameras.main.shake(5000, .05)
        window.scene.tweens.add({
            targets: window.scene.music,
            volume: 0,
            duration: 3000
        })
        let final = window.scene.sound.add(ASSET_KEYS.CRY2)
        final.on('complete', ()=>{
            window.scene.rho.destroy()
        })
        final.play()
    }
  }
}