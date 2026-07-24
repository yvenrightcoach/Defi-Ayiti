/**
 * Sons du jeu : quelques effets synthetises en direct via l'API Web Audio
 * (pas de fichier a charger), et de vrais fichiers audio pour la musique
 * du menu et les reponses correctes/incorrectes.
 */

type ToneType = OscillatorType;

interface Tone {
  freq: number;
  start: number;
  duration: number;
  type?: ToneType;
  peak?: number;
}

let ctx: AudioContext | null = null;
let enabled = true;

export function setSoundEnabled(value: boolean) {
  enabled = value;
  if (!value) menuMusic?.pause();
}

function getContext(): AudioContext | null {
  if (typeof window === "undefined") return null;
  const AudioCtx = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AudioCtx) return null;
  if (!ctx) ctx = new AudioCtx();
  if (ctx.state === "suspended") void ctx.resume();
  return ctx;
}

function playTones(tones: Tone[]) {
  if (!enabled) return;
  const audioCtx = getContext();
  if (!audioCtx) return;
  const now = audioCtx.currentTime;

  for (const tone of tones) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = tone.type ?? "sine";
    osc.frequency.value = tone.freq;

    const startAt = now + tone.start;
    const endAt = startAt + tone.duration;
    const peak = tone.peak ?? 0.2;

    gain.gain.setValueAtTime(0, startAt);
    gain.gain.linearRampToValueAtTime(peak, startAt + Math.min(0.015, tone.duration / 4));
    gain.gain.exponentialRampToValueAtTime(0.001, endAt);

    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(startAt);
    osc.stop(endAt + 0.02);
  }
}

// --- Fichiers audio (correct / faux / musique du menu) ---------------------

const audioCache = new Map<string, HTMLAudioElement>();

function getAudio(src: string): HTMLAudioElement {
  let audio = audioCache.get(src);
  if (!audio) {
    audio = new Audio(src);
    audio.preload = "auto";
    audioCache.set(src, audio);
  }
  return audio;
}

function playFile(src: string, volume: number) {
  if (!enabled) return;
  const audio = getAudio(src);
  audio.volume = volume;
  audio.currentTime = 0;
  void audio.play().catch(() => {
    // Lecture bloquee (politique d'autoplay) : ignore silencieusement,
    // le prochain geste utilisateur permettra de reessayer naturellement.
  });
}

let menuMusic: HTMLAudioElement | null = null;

/** Musique de fond de l'ecran de connexion/menu, en boucle. */
export function playMenuMusic() {
  if (!enabled) return;
  if (!menuMusic) {
    menuMusic = getAudio("/sounds/menu-theme.mp3");
    menuMusic.loop = true;
    menuMusic.volume = 0.35;
  }
  menuMusic.play().catch(() => {
    // Autoplay bloque avant tout geste utilisateur : on retente au premier
    // clic/touch, pattern standard pour la musique de fond.
    const retry = () => {
      void menuMusic?.play().catch(() => {});
    };
    document.addEventListener("click", retry, { once: true });
    document.addEventListener("touchstart", retry, { once: true });
  });
}

export function stopMenuMusic() {
  if (!menuMusic) return;
  menuMusic.pause();
  menuMusic.currentTime = 0;
}

/** Petit clic doux, joue sur les boutons et tuiles de l'interface. */
export function playClick() {
  playTones([{ freq: 720, start: 0, duration: 0.06, type: "sine", peak: 0.12 }]);
}

/** Reponse correcte. */
export function playCorrect() {
  playFile("/sounds/correct.mp3", 0.6);
}

/** Mauvaise reponse. */
export function playWrong() {
  playFile("/sounds/wrong.mp3", 0.5);
}

/** Fanfare courte (3 notes), fin de niveau/match reussie. */
export function playSuccess() {
  playTones([
    { freq: 523.25, start: 0, duration: 0.13, type: "triangle", peak: 0.22 },
    { freq: 659.25, start: 0.12, duration: 0.13, type: "triangle", peak: 0.22 },
    { freq: 987.77, start: 0.24, duration: 0.3, type: "triangle", peak: 0.24 },
  ]);
}

/** Piece/recompense, deux blips aigus rapides. */
export function playCoin() {
  playTones([
    { freq: 988, start: 0, duration: 0.06, type: "square", peak: 0.15 },
    { freq: 1319, start: 0.05, duration: 0.09, type: "square", peak: 0.15 },
  ]);
}

/** Arpege scintillant, deblocage d'un heros. */
export function playUnlock() {
  playTones([
    { freq: 659.25, start: 0, duration: 0.1, type: "triangle", peak: 0.2 },
    { freq: 830.61, start: 0.08, duration: 0.1, type: "triangle", peak: 0.2 },
    { freq: 1046.5, start: 0.16, duration: 0.1, type: "triangle", peak: 0.2 },
    { freq: 1318.51, start: 0.24, duration: 0.35, type: "triangle", peak: 0.24 },
  ]);
}
