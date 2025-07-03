import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTimerStore = defineStore('timer', () => {
  const isTracking = ref(false)
  const elapsedSeconds = ref(0)
  const startTime = ref(null)
  const timerInterval = ref(null)
  const isPomodoro = ref(false)
  const countdownSeconds = ref(25 * 60)

  const formattedElapsed = computed(() => {
    const h = String(Math.floor(elapsedSeconds.value / 3600)).padStart(2, '0')
    const m = String(Math.floor((elapsedSeconds.value % 3600) / 60)).padStart(2, '0')
    const s = String(elapsedSeconds.value % 60).padStart(2, '0')
    return `${h}:${m}:${s}`
  })

  const formattedCountdown = computed(() => {
    const m = String(Math.floor(countdownSeconds.value / 60)).padStart(2, '0')
    const s = String(countdownSeconds.value % 60).padStart(2, '0')
    return `${m}:${s}`
  })

  function startTracking() {
    isTracking.value = true
    startTime.value = new Date()
    elapsedSeconds.value = 0
    
    if (timerInterval.value) clearInterval(timerInterval.value)
    
    timerInterval.value = setInterval(() => {
      elapsedSeconds.value++
    }, 1000)
  }

  function startPomodoro() {
    isPomodoro.value = true
    countdownSeconds.value = 50 * 60
    
    if (timerInterval.value) clearInterval(timerInterval.value)
    
    timerInterval.value = setInterval(() => {
      countdownSeconds.value--
      if (countdownSeconds.value <= 0) {
        stopPomodoro()
      }
    }, 1000)
  }

  function stopPomodoro() {
    clearInterval(timerInterval.value)
    isPomodoro.value = false
  }

  async function stopTracking() {
    clearInterval(timerInterval.value)
    isTracking.value = false
    
    const endTime = new Date()
    const duration = elapsedSeconds.value
    
    // Reset
    elapsedSeconds.value = 0
    startTime.value = null
    timerInterval.value = null
    
    return { 
      start: startTime.value, 
      end: endTime, 
      duration,
      type: isPomodoro.value ? 'pomodoro' : 'study' 
    }
  }

  return {
    isTracking,
    elapsedSeconds,
    startTime,
    isPomodoro,
    countdownSeconds,
    formattedElapsed,
    formattedCountdown,
    startTracking,
    stopTracking,
    startPomodoro,
    stopPomodoro
  }
})