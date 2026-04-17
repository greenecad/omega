import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from '../common/scene-keys.js';
import { ASSET_KEYS } from '../common/assets.js';

export class TargetPracticeScene extends Phaser.Scene {
  constructor() {
    super(SCENE_KEYS.TARGET_PRACTICE_SCENE);
  }
  create() {
    window.score = 0;
    this.scoreText = this.add.text(10, 10, `Score: ${window.score}`, { fontSize: '16px', fill: '#fff' });
    this.timerText = this.add.text(10, 30, `Time: 15.00`, { fontSize: '16px', fill: '#fff' });
    let x = Phaser.Math.Between(50, 750);
    let y = Phaser.Math.Between(50, 550);
    this.target = this.physics.add.sprite(x, y, ASSET_KEYS.TARGET).setInteractive().setScale(.15);
    this.startText = this.add.text(10, 50, 'Click the target to start the timer.', { fontSize: '16px', fill: '#fff' });
    this.started = false;
    if(determination){
        this.target.setScale(.2);
        this.add.text(10, 70, 'you feel a sense of DETERMINATION.', { fontSize: '16px', fill: '#fff' });
    }
    this.target.on('pointerdown', () => {
      window.score+=10;
      this.scoreText.setText(`Score: ${window.score}`);
      this.target.x = Phaser.Math.Between(50, 750);
      this.target.y = Phaser.Math.Between(50, 550);
      this.time.delayedCall(15000, () => {
        this.scene.pause(SCENE_KEYS.TARGET_PRACTICE_SCENE);
        const submitButton = document.getElementById('submit-button');
        if (submitButton) {
            submitButton.style.display = 'block';
        }
      });
      this.startText.setText('');
      this.started = true;
    });
    this.timer = 15000;
  }
  update() {
    if (this.started) {
    this.timer -= this.game.loop.delta;
    this.timerText.setText(`Time: ${Math.max(0, this.timer / 1000).toFixed(2)}`);
    }
  }
}

let submitScore = () => {
  
  console.log('Submitting score:', window.score);
  document.getElementById("score-input").value = window.score;
  document.getElementById("score-form").submit();
}

window.submitScore = submitScore;