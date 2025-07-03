<script setup>
import { useTimerStore } from '@/stores/timerStore'
import { computed } from 'vue'

const timerStore = useTimerStore()

const timerText = computed(() => {
  return timerStore.isPomodoro 
    ? `🍅 ${timerStore.formattedCountdown}`
    : `⏱️ ${timerStore.formattedElapsed}`
})

const timerClass = computed(() => {
  return timerStore.isPomodoro ? 'pomodoro' : 'study'
})
</script>

<template>
  <div v-if="timerStore.isTracking || timerStore.isPomodoro" 
       :class="['floating-timer', timerClass]">
    <span class="timer-text">{{ timerText }}</span>
    <button class="stop-btn" @click="timerStore.isPomodoro ? timerStore.stopPomodoro() : timerStore.stopTracking()">
      Dừng
    </button>
  </div>
</template>

<style scoped>
.floating-timer {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 10px 15px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.floating-timer.study {
  border-left: 4px solid #4CAF50;
}

.floating-timer.pomodoro {
  border-left: 4px solid #FF5252;
}

.timer-text {
  font-size: 1rem;
}

.stop-btn {
  background: #FF5252;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 0.8rem;
}

.stop-btn:hover {
  background: #FF0000;
}
</style>