import './style.css'
import Sortable from 'sortablejs'
import gameData from './data.json'

// ── Constants ──
const CARDS_PER_ROUND = 5
const POINTS_FIRST_TRY = 5
const PENALTY_PER_ERROR = 1
const MAX_ERRORS_PER_LEVEL = 5
const STARTING_LIVES = 3
const STORAGE_KEY = 'path-of-all-things-highscore'
const MUSIC_VOLUME_KEY = 'path-of-all-things-music'

// ── State ──
const state = {
  currentLevel: 0,
  levels: gameData.levels,
  activeEvents: [],
  sortableInstance: null,
  isRevealed: false,
  score: 0,
  levelErrors: 0,
  lives: STARTING_LIVES,
  highScore: loadHighScore(),
  musicPlaying: false,
}

const app = document.getElementById('app')
const progressDots = document.getElementById('progress-dots')
const inkBleed = document.getElementById('ink-bleed')

// ── Audio ──
const BASE = import.meta.env.BASE_URL

const bgMusic = new Audio(`${BASE}music.mp3`)
bgMusic.loop = true
bgMusic.volume = 0.12
bgMusic.preload = 'auto'

// Sound effects
const sfx = {
  cardMove:   new Audio(`${BASE}Card movement - Epidemic Sound.wav`),
  incorrect:  new Audio(`${BASE}Incorrect_Wood Impact.mp3`),
  correct:    new Audio(`${BASE}All 5 Correct_Japanese Instrument.wav`),
  modalOpen:  new Audio(`${BASE}Modal Open - Epidemic Sound.wav`),
  nextLevel:  new Audio(`${BASE}Next Level_Bamboo Chimes.wav`),
  finishGame: new Audio(`${BASE}Finish Game_Temple Bowl.wav`),
  gameStart:  new Audio(`${BASE}Game start_crystal bowl.wav`),
}

// Set volumes
sfx.cardMove.volume = 0.6
sfx.incorrect.volume = 0.6
sfx.correct.volume = 0.6
sfx.modalOpen.volume = 0.6
sfx.nextLevel.volume = 0.6
sfx.finishGame.volume = 0.6
sfx.gameStart.volume = 0.6

// Preload all SFX
Object.values(sfx).forEach(s => { s.preload = 'auto' })

// SFX plays regardless of mute (mute only controls music)
function playSFX(sound) {
  sound.currentTime = 0
  sound.play().catch(() => {})
}

// Play a sound and fade it out over its last N ms
function playSFXWithFade(sound, fadeDuration = 2000) {
  sound.currentTime = 0
  sound.play().then(() => {
    const schedFade = () => {
      const remaining = (sound.duration - sound.currentTime) * 1000
      if (remaining <= fadeDuration) {
        fadeOutAudio(sound, remaining)
      } else {
        setTimeout(() => fadeOutAudio(sound, fadeDuration), remaining - fadeDuration)
      }
    }
    if (sound.duration && isFinite(sound.duration)) {
      schedFade()
    } else {
      sound.addEventListener('loadedmetadata', schedFade, { once: true })
    }
  }).catch(() => {})
}

// Fade music volume from 0 to target over duration
function fadeInMusic(target, durationMs) {
  bgMusic.volume = 0
  bgMusic.play().then(() => {
    state.musicPlaying = true
    updateMusicButton()
    const steps = 40
    const increment = target / steps
    let vol = 0
    const fade = setInterval(() => {
      vol += increment
      if (vol >= target) {
        bgMusic.volume = target
        clearInterval(fade)
      } else {
        bgMusic.volume = vol
      }
    }, durationMs / steps)
  }).catch(() => {})
}

// Fade out an audio element over durationMs, then pause & reset volume
function fadeOutAudio(audio, durationMs, onComplete) {
  const startVol = audio.volume
  const steps = 30
  const decrement = startVol / steps
  let vol = startVol
  const fade = setInterval(() => {
    vol -= decrement
    if (vol <= 0) {
      audio.volume = 0
      audio.pause()
      audio.volume = startVol  // reset for next play
      clearInterval(fade)
      if (onComplete) onComplete()
    } else {
      audio.volume = vol
    }
  }, durationMs / steps)
}

// Play crystal bowl then optionally fade in music
function playStartSequence(enableMusic) {
  playSFX(sfx.gameStart)

  // Fade bowl out over its last 2 seconds
  const bowl = sfx.gameStart
  const fadeDuration = 2000

  const startFadeOut = () => {
    const remaining = (bowl.duration - bowl.currentTime) * 1000
    if (remaining <= fadeDuration) {
      // Already within fade window — start immediately
      fadeOutAudio(bowl, remaining, enableMusic ? () => fadeInMusic(0.12, 2000) : null)
    } else {
      // Wait until we're fadeDuration ms from the end
      const delay = remaining - fadeDuration
      setTimeout(() => {
        fadeOutAudio(bowl, fadeDuration, enableMusic ? () => fadeInMusic(0.12, 2000) : null)
      }, delay)
    }
  }

  // duration may not be loaded yet
  if (bowl.duration && isFinite(bowl.duration)) {
    startFadeOut()
  } else {
    bowl.addEventListener('loadedmetadata', startFadeOut, { once: true })
  }
}

function toggleMusic() {
  if (state.musicPlaying) {
    bgMusic.pause()
    state.musicPlaying = false
    localStorage.setItem(MUSIC_VOLUME_KEY, 'muted')
  } else {
    bgMusic.play().then(() => {
      bgMusic.volume = 0.12
      state.musicPlaying = true
      localStorage.setItem(MUSIC_VOLUME_KEY, 'on')
    })
  }
  updateMusicButton()
}

function updateMusicButton() {
  const btn = document.getElementById('music-toggle')
  if (btn) btn.textContent = state.musicPlaying ? '\u266B' : '\u266C'
  if (btn) btn.title = state.musicPlaying ? 'Mute music' : 'Play music'
  if (btn) btn.classList.toggle('muted', !state.musicPlaying)
}

// ── Start Screen ──
function showStartScreen() {
  const hud = document.querySelector('.hud')
  if (hud) hud.style.opacity = '0'

  const saved = localStorage.getItem(MUSIC_VOLUME_KEY)
  let musicOn = saved !== 'muted'

  const overlay = document.createElement('div')
  overlay.className = 'start-overlay'
  overlay.innerHTML = `
    <div class="start-card">
      <div class="start-symbol">\u25CC</div>
      <h1 class="start-title">The Path of All Things</h1>
      <div class="start-divider"></div>
      <p class="start-description">
        From the first light to the last silence,<br>
        trace the thread that binds all things.<br>
        Arrange the moments. Find the order.
      </p>
      <button class="start-music-toggle" id="start-music-toggle">
        \u266B Music: ${musicOn ? 'On' : 'Off'}
      </button>
      <button class="btn-contemplate start-begin" id="btn-begin">
        Begin
      </button>
    </div>
  `

  document.body.appendChild(overlay)

  // Music toggle on start screen
  const musicBtn = overlay.querySelector('#start-music-toggle')
  musicBtn.addEventListener('click', () => {
    musicOn = !musicOn
    musicBtn.textContent = `\u266B Music: ${musicOn ? 'On' : 'Off'}`
    musicBtn.classList.toggle('off', !musicOn)
  })

  // Begin button
  overlay.querySelector('#btn-begin').addEventListener('click', () => {
    // Save music preference
    localStorage.setItem(MUSIC_VOLUME_KEY, musicOn ? 'on' : 'muted')

    // Play crystal bowl + start music if enabled
    playStartSequence(musicOn)

    // Fade out start screen
    overlay.classList.add('closing')
    setTimeout(() => {
      overlay.remove()

      // Show HUD
      if (hud) {
        hud.style.opacity = '1'
        hud.style.transition = 'opacity 0.8s ease'
      }

      // Start the game
      renderProgressDots()
      renderLevel()
      updateMusicButton()
    }, 600)
  })
}

// ── High Score (localStorage) ──
function loadHighScore() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? parseInt(saved, 10) : 0
  } catch {
    return 0
  }
}

function saveHighScore(score) {
  try {
    if (score > state.highScore) {
      state.highScore = score
      localStorage.setItem(STORAGE_KEY, String(score))
    }
  } catch {
    // localStorage unavailable — silent fail
  }
}

// ── Utilities ──
function shuffleArray(arr) {
  const shuffled = [...arr]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

function pickRandomEvents(events, count) {
  const shuffled = shuffleArray(events)
  return shuffled.slice(0, count)
}

// ── Year Formatter ──
function formatYear(year) {
  const abs = Math.abs(year)
  const suffix = year < 0 ? 'ago' : 'from now'

  if (abs >= 1e20) {
    const exp = Math.floor(Math.log10(abs))
    return `10${toSuperscript(exp)} years ${suffix}`
  }
  if (abs >= 1e12) {
    return `${formatDecimal(abs / 1e12)} trillion years ${suffix}`
  }
  if (abs >= 1e9) {
    return `${formatDecimal(abs / 1e9)} billion years ${suffix}`
  }
  if (abs >= 1e6) {
    return `${formatDecimal(abs / 1e6)} million years ${suffix}`
  }
  if (abs >= 10000) {
    return `~${Math.round(abs / 1000).toLocaleString()},000 years ${suffix}`
  }
  if (year < 0) {
    return `${abs.toLocaleString()} BCE`
  }
  return `${year} CE`
}

function formatDecimal(n) {
  return n % 1 === 0 ? n.toString() : n.toFixed(1)
}

function toSuperscript(num) {
  const superscripts = { '0': '\u2070', '1': '\u00b9', '2': '\u00b2', '3': '\u00b3', '4': '\u2074', '5': '\u2075', '6': '\u2076', '7': '\u2077', '8': '\u2078', '9': '\u2079' }
  return String(num).split('').map(d => superscripts[d] || d).join('')
}

// ── Render Progress Dots ──
function renderProgressDots() {
  progressDots.innerHTML = state.levels
    .map((_, i) => {
      let cls = 'progress-dot'
      if (i < state.currentLevel) cls += ' completed'
      if (i === state.currentLevel) cls += ' active'
      return `<div class="${cls}"></div>`
    })
    .join('')
}

// ── Render HUD ──
function renderHUD() {
  // Score
  const el = document.getElementById('score-display')
  if (el) el.textContent = state.score
  const hi = document.getElementById('highscore-display')
  if (hi) hi.textContent = state.highScore

  // Lives
  const livesEl = document.getElementById('lives-display')
  if (livesEl) {
    livesEl.innerHTML = Array.from({ length: STARTING_LIVES }, (_, i) => {
      const alive = i < state.lives
      return `<span class="life-pip ${alive ? 'alive' : 'spent'}">\u25C6</span>`
    }).join('')
  }
}

// ── Create Card HTML ──
function createCardHTML(event) {
  return `
    <div class="card card-enter" data-id="${event.id}">
      <div class="card-glow"></div>
      <div class="card-inner">
        <div class="card-edge-top"></div>
        <div class="card-content">
          <h3 class="card-title">${event.title}</h3>
          <p class="card-flavor">${event.description}</p>
          <div class="card-year">${formatYear(event.year)}</div>
        </div>
        <div class="card-edge-bottom"></div>
      </div>
    </div>
  `
}

// ── Image path helper ──
function getEventImagePath(event) {
  const safeTitle = event.title.replace(/ /g, '_').replace(/\//g, '-').replace(/'/g, '')
  return `${BASE}images/${event.id}_${safeTitle}.webp`
}

// ── Info Modal ──
function showInfoModal(event) {
  const existing = document.querySelector('.modal-overlay')
  if (existing) existing.remove()

  const bodyHTML = (event.info || 'No additional information available.')
    .split('\n\n')
    .map(p => `<p>${p}</p>`)
    .join('')

  const imagePath = getEventImagePath(event)

  const overlay = document.createElement('div')
  overlay.className = 'modal-overlay'
  overlay.innerHTML = `
    <div class="modal-card">
      <button class="modal-close" aria-label="Close">&times;</button>
      <div class="modal-header">
        <div class="modal-title">${event.title}</div>
        <div class="modal-year">${formatYear(event.year)}</div>
      </div>
      <div class="modal-divider"></div>
      <div class="modal-columns">
        <div class="modal-image">
          <img src="${imagePath}" alt="${event.title}" class="modal-img" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'modal-image-placeholder',innerHTML:'<span class=\\'modal-image-icon\\'>&#x25CC;</span>'}))" />
        </div>
        <div class="modal-body">${bodyHTML}</div>
      </div>
    </div>
  `

  document.body.appendChild(overlay)
  playSFX(sfx.modalOpen)

  function closeModal() {
    playSFX(sfx.modalOpen)
    overlay.classList.add('closing')
    setTimeout(() => overlay.remove(), 300)
  }

  overlay.querySelector('.modal-close').addEventListener('click', closeModal)
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal()
  })
}

// ── Reveal Correct Order ──
// Sorts cards into correct order in the DOM, then reveals them
function revealCorrectOrder(feedbackMsg, feedbackColor) {
  state.isRevealed = true

  const cardList = document.getElementById('card-list')
  const cards = [...cardList.querySelectorAll('.card')]
  const feedback = document.getElementById('feedback')

  // Disable sorting immediately
  if (state.sortableInstance) {
    state.sortableInstance.option('disabled', true)
  }

  const correctOrder = [...state.activeEvents]
    .sort((a, b) => a.year - b.year)
    .map(e => e.id)

  // Rearrange DOM to correct order
  correctOrder.forEach(id => {
    const card = cards.find(c => parseInt(c.dataset.id) === id)
    if (card) cardList.appendChild(card)
  })

  // Re-query after DOM rearrange
  const sortedCards = [...cardList.querySelectorAll('.card')]

  feedback.textContent = feedbackMsg
  feedback.style.opacity = '1'
  feedback.style.color = feedbackColor

  renderHUD()

  // Stagger reveal + attach click handlers for info modals
  sortedCards.forEach((card, i) => {
    setTimeout(() => {
      card.classList.add('revealed', 'correct')
    }, i * 200)

    card.addEventListener('click', () => {
      if (!card.classList.contains('revealed')) return
      const eventId = parseInt(card.dataset.id)
      const event = state.activeEvents.find(e => e.id === eventId)
      if (event) showInfoModal(event)
    })
  })

  // Show next/complete button
  const btn = document.getElementById('btn-check')
  setTimeout(() => {
    if (state.currentLevel < state.levels.length - 1) {
      btn.textContent = 'Continue'
      btn.removeEventListener('click', checkOrder)
      btn.addEventListener('click', nextLevel)
    } else {
      btn.textContent = 'Complete'
      btn.removeEventListener('click', checkOrder)
      btn.addEventListener('click', showCompletion)
    }
  }, sortedCards.length * 200 + 400)
}

// ── Render Level ──
function renderLevel() {
  const level = state.levels[state.currentLevel]
  state.activeEvents = pickRandomEvents(level.events, CARDS_PER_ROUND)
  const shuffledEvents = shuffleArray(state.activeEvents)
  state.isRevealed = false
  state.levelErrors = 0

  app.innerHTML = `
    <div class="text-center mb-12">
      <h1 class="level-title text-3xl md:text-4xl font-semibold tracking-wide" style="font-family: var(--font-serif);">
        ${level.name}
      </h1>
      <p class="level-subtitle mt-3 text-base italic opacity-50" style="font-family: var(--font-serif);">
        ${level.subtitle}
      </p>
      <p class="level-subtitle mt-6 text-xs tracking-[0.2em] uppercase opacity-30">
        Arrange from earliest to latest
      </p>
    </div>

    <div class="relative w-full max-w-lg mx-auto">
      <div class="timeline-line"></div>
      <div id="card-list" class="relative z-10 flex flex-col items-center gap-3 px-2">
        ${shuffledEvents.map(e => createCardHTML(e)).join('')}
      </div>
    </div>

    <div class="mt-10 flex flex-col items-center gap-4">
      <button class="btn-contemplate" id="btn-check">
        Contemplate
      </button>
      <p id="feedback" class="text-sm italic opacity-0 transition-opacity duration-700" style="font-family: var(--font-serif);">
        &nbsp;
      </p>
    </div>
  `

  // Init SortableJS
  const cardList = document.getElementById('card-list')
  if (state.sortableInstance) state.sortableInstance.destroy()

  state.sortableInstance = Sortable.create(cardList, {
    animation: 450,
    easing: 'cubic-bezier(0.23, 1, 0.32, 1)',
    ghostClass: 'sortable-ghost',
    chosenClass: 'sortable-chosen',
    dragClass: 'sortable-drag',
    delay: 50,
    delayOnTouchOnly: true,
    onEnd: () => playSFX(sfx.cardMove),
  })

  document.getElementById('btn-check').addEventListener('click', checkOrder)
  renderHUD()
}

// ── Check Order ──
function checkOrder() {
  if (state.isRevealed) return

  const cardList = document.getElementById('card-list')
  const cards = [...cardList.querySelectorAll('.card')]
  const currentOrder = cards.map(c => parseInt(c.dataset.id))

  const correctOrder = [...state.activeEvents]
    .sort((a, b) => a.year - b.year)
    .map(e => e.id)

  const isCorrect = currentOrder.every((id, i) => id === correctOrder[i])
  const feedback = document.getElementById('feedback')

  if (isCorrect) {
    // Calculate score for this level
    const levelScore = Math.max(0, POINTS_FIRST_TRY - (state.levelErrors * PENALTY_PER_ERROR))
    state.score += levelScore

    let msg = ''
    if (state.levelErrors === 0) {
      msg = 'Perfect clarity. +5'
    } else if (levelScore > 0) {
      msg = `The path reveals itself. +${levelScore}`
    } else {
      msg = 'The path reveals itself, at last.'
    }

    playSFX(sfx.correct)
    revealCorrectOrder(msg, 'var(--color-moss)')
  } else {
    state.levelErrors++
    playSFX(sfx.incorrect)

    // 5th error — lose a life, auto-reveal
    if (state.levelErrors >= MAX_ERRORS_PER_LEVEL) {
      state.lives--
      renderHUD()

      // Check for game over
      if (state.lives <= 0) {
        // Brief pause to let the life disappear register, then game over
        setTimeout(() => showGameOver(), 1200)
        // Still reveal the answer first
        revealCorrectOrder('The path was beyond reach. A light fades.', 'var(--color-rust)')
        return
      }

      revealCorrectOrder('The path reveals itself, but a light fades.', 'var(--color-rust)')
      return
    }

    const attemptsLeft = MAX_ERRORS_PER_LEVEL - state.levelErrors
    const remaining = Math.max(0, POINTS_FIRST_TRY - (state.levelErrors * PENALTY_PER_ERROR))

    let msg = ''
    if (remaining > 0) {
      msg = `Not quite. ${remaining} point${remaining !== 1 ? 's' : ''} remaining. ${attemptsLeft} attempt${attemptsLeft !== 1 ? 's' : ''} left.`
    } else {
      msg = `No points remain. ${attemptsLeft} attempt${attemptsLeft !== 1 ? 's' : ''} before the path reveals itself.`
    }

    feedback.textContent = msg
    feedback.style.opacity = '1'
    feedback.style.color = 'var(--color-rust)'

    // Only highlight cards that are in the wrong position
    cards.forEach((card, i) => {
      if (currentOrder[i] !== correctOrder[i]) {
        card.classList.add('wrong')
      }
    })
    setTimeout(() => {
      cards.forEach(card => card.classList.remove('wrong'))
    }, 3700)

    setTimeout(() => {
      feedback.style.opacity = '0'
    }, 3000)
  }
}

// ── Next Level ──
function nextLevel() {
  playSFX(sfx.nextLevel)
  inkBleed.classList.add('active')

  setTimeout(() => {
    state.currentLevel++
    renderProgressDots()
    renderLevel()

    setTimeout(() => {
      inkBleed.classList.remove('active')
    }, 300)
  }, 1200)
}

// ── Game Over Screen ──
function showGameOver() {
  saveHighScore(state.score)
  const isNewRecord = state.score > 0 && state.score >= state.highScore

  playSFXWithFade(sfx.finishGame, 2000)
  inkBleed.classList.add('active')

  setTimeout(() => {
    app.innerHTML = `
      <div class="completion-message text-center max-w-lg">
        <h1 class="text-4xl md:text-5xl font-semibold tracking-wide mb-6" style="font-family: var(--font-serif); color: var(--color-rust);">
          The Path Fades
        </h1>
        <p class="text-lg italic opacity-60 leading-relaxed mb-8" style="font-family: var(--font-serif);">
          All lights have dimmed. The thread slips from your hands,<br>
          but the path remains, patient, for those who return.
        </p>

        <div class="score-final">
          <div class="text-5xl font-semibold" style="color: var(--color-gold); font-family: var(--font-serif);">
            ${state.score}
          </div>
          <div class="mt-2 text-xs tracking-[0.2em] uppercase opacity-40">
            points earned
          </div>
          ${isNewRecord ? `
            <div class="mt-3 text-sm tracking-[0.15em]" style="color: var(--color-moss);">
              \u2726 New High Score \u2726
            </div>
          ` : state.highScore > 0 ? `
            <div class="mt-3 text-xs opacity-30">
              Best: ${state.highScore}
            </div>
          ` : ''}
        </div>

        <button class="btn-contemplate mt-10" id="btn-restart">
          Begin Again
        </button>
      </div>
    `

    document.getElementById('btn-restart').addEventListener('click', () => {
      playSFX(sfx.gameStart)
      inkBleed.classList.add('active')
      setTimeout(() => {
        state.currentLevel = 0
        state.score = 0
        state.levelErrors = 0
        state.lives = STARTING_LIVES
        renderProgressDots()
        renderLevel()
        setTimeout(() => inkBleed.classList.remove('active'), 300)
      }, 1200)
    })

    setTimeout(() => inkBleed.classList.remove('active'), 300)
  }, 1200)
}

// ── Completion Screen ──
function showCompletion() {
  saveHighScore(state.score)
  const isNewRecord = state.score >= state.highScore

  playSFXWithFade(sfx.finishGame, 2000)
  inkBleed.classList.add('active')

  setTimeout(() => {
    app.innerHTML = `
      <div class="completion-message text-center max-w-lg">
        <h1 class="text-4xl md:text-5xl font-semibold tracking-wide mb-6" style="font-family: var(--font-serif);">
          The Path is Walked
        </h1>
        <p class="text-lg italic opacity-60 leading-relaxed mb-8" style="font-family: var(--font-serif);">
          From the first light to the last silence,<br>
          you have traced the thread that binds all things.
        </p>

        <div class="score-final">
          <div class="text-5xl font-semibold" style="color: var(--color-gold); font-family: var(--font-serif);">
            ${state.score}
          </div>
          <div class="mt-2 text-xs tracking-[0.2em] uppercase opacity-40">
            points earned
          </div>
          <div class="mt-1 text-xs opacity-25">
            ${state.lives} ${state.lives === 1 ? 'light' : 'lights'} remaining
          </div>
          ${isNewRecord ? `
            <div class="mt-3 text-sm tracking-[0.15em]" style="color: var(--color-moss);">
              \u2726 New High Score \u2726
            </div>
          ` : `
            <div class="mt-3 text-xs opacity-30">
              Best: ${state.highScore}
            </div>
          `}
        </div>

        <div class="mt-10 opacity-20 text-sm tracking-[0.2em] uppercase">
          13.8 billion years, contemplated
        </div>
        <button class="btn-contemplate mt-10" id="btn-restart">
          Begin Again
        </button>
      </div>
    `

    document.getElementById('btn-restart').addEventListener('click', () => {
      playSFX(sfx.gameStart)
      inkBleed.classList.add('active')
      setTimeout(() => {
        state.currentLevel = 0
        state.score = 0
        state.levelErrors = 0
        state.lives = STARTING_LIVES
        renderProgressDots()
        renderLevel()
        setTimeout(() => inkBleed.classList.remove('active'), 300)
      }, 1200)
    })

    setTimeout(() => inkBleed.classList.remove('active'), 300)
  }, 1200)
}

// ── Init ──
document.getElementById('music-toggle').addEventListener('click', toggleMusic)
showStartScreen()

function initEmbers() {
  const canvas = document.getElementById('embers-canvas');
  const ctx = canvas.getContext('2d');

  let width, height, particles;

  // Configuration
  const particleCount = 40;
  const colors = ['#c4a882', '#e8e0d4', '#8c7a5d']; // Gold, Off-white, Dim gold

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  class Particle {
    constructor() {
      this.reset();
    }

    reset() {
      this.x = Math.random() * width;
      this.y = height + Math.random() * 100; // Start below screen
      this.size = Math.random() * 2 + 0.5;
      this.speedY = Math.random() * 0.4 + 0.1; // Slow drift
      this.speedX = Math.random() * 0.2 - 0.1;
      this.opacity = Math.random() * 0.5 + 0.1;
      this.color = colors[Math.floor(Math.random() * colors.length)];
      this.oscillation = Math.random() * 100; // For swaying
    }

    update() {
      this.y -= this.speedY;
      // Gentle swaying movement
      this.x += Math.sin(this.y / 50 + this.oscillation) * 0.2;

      // If it goes off top, reset to bottom
      if (this.y < -10) {
        this.reset();
      }
    }

    draw() {
      ctx.globalAlpha = this.opacity;
      ctx.fillStyle = this.color;
      ctx.beginPath();
      // Use a soft circle for a "glow" feel
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function init() {
    resize();
    particles = Array.from({ length: particleCount }, () => new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize);
  init();
  animate();
}

// Call the function
initEmbers();