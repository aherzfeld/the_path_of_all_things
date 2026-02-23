// ── Floating Embers — Canvas Particle System ──

const EMBER_COUNT = 40
const COLORS = ['#c4a882', '#e8e0d4']

class Ember {
  constructor(w, h) {
    this.reset(w, h, true)
  }

  reset(w, h, randomY = false) {
    this.x = Math.random() * w
    this.y = randomY ? Math.random() * h : h + Math.random() * 40
    this.size = 1 + Math.random() * 2
    this.speedY = 0.15 + Math.random() * 0.35
    this.drift = Math.random() * Math.PI * 2
    this.driftSpeed = 0.002 + Math.random() * 0.004
    this.driftAmp = 8 + Math.random() * 16
    this.alpha = 0
    this.maxAlpha = 0.15 + Math.random() * 0.3
    this.fadeIn = 0.002 + Math.random() * 0.003
    this.color = COLORS[Math.floor(Math.random() * COLORS.length)]
    this.blur = 0.5 + Math.random() * 1.5
    this.life = 0
  }
}

export function initBackground() {
  const canvas = document.createElement('canvas')
  canvas.id = 'ember-canvas'
  canvas.style.cssText = `
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
    width: 100%;
    height: 100%;
  `
  document.body.prepend(canvas)

  const ctx = canvas.getContext('2d')
  let w, h
  const embers = []

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    w = window.innerWidth
    h = window.innerHeight
    canvas.width = w * dpr
    canvas.height = h * dpr
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  function init() {
    resize()
    for (let i = 0; i < EMBER_COUNT; i++) {
      embers.push(new Ember(w, h))
    }
  }

  function draw() {
    ctx.clearRect(0, 0, w, h)

    for (const e of embers) {
      e.life++
      e.y -= e.speedY
      e.drift += e.driftSpeed
      const sway = Math.sin(e.drift) * e.driftAmp

      // Fade in, hold, fade out near top
      const normalY = 1 - e.y / h
      if (normalY < 0.1) {
        e.alpha = Math.min(e.alpha + e.fadeIn, e.maxAlpha * (normalY / 0.1))
      } else if (normalY > 0.85) {
        e.alpha = e.maxAlpha * (1 - (normalY - 0.85) / 0.15)
      } else {
        e.alpha = Math.min(e.alpha + e.fadeIn, e.maxAlpha)
      }

      if (e.y < -20) {
        e.reset(w, h)
        continue
      }

      ctx.save()
      ctx.globalAlpha = Math.max(0, e.alpha)
      ctx.filter = `blur(${e.blur}px)`
      ctx.fillStyle = e.color
      ctx.beginPath()
      ctx.arc(e.x + sway, e.y, e.size, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()
    }

    requestAnimationFrame(draw)
  }

  window.addEventListener('resize', () => {
    resize()
  })

  init()
  requestAnimationFrame(draw)
}
